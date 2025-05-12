"""
InfluxDB client for time-series data operations.
Provides a robust interface for writing and querying time-series data with proper connection management.
"""

from typing import Any, Dict, List, Optional, Union
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from influxdb_client.client.query_api import QueryApi
from django.conf import settings
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

def handle_influx_errors(func):
    """Decorator to handle InfluxDB operation errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"InfluxDB operation failed: {e}")
            raise
    return wrapper

class InfluxDBClient:
    """Client for interacting with InfluxDB time-series database."""
    
    def __init__(
        self,
        url: str = settings.INFLUXDB_URL,
        token: str = settings.INFLUXDB_TOKEN,
        org: str = settings.INFLUXDB_ORG,
        default_bucket: str = settings.INFLUXDB_BUCKET,
        batch_size: int = 1000,
        flush_interval: int = 10_000
    ):
        """Initialize InfluxDB client with connection parameters."""
        self.url = url
        self.token = token
        self.org = org
        self.default_bucket = default_bucket
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self._client: Optional[InfluxDBClient] = None
        self._write_api: Optional[WriteApi] = None
        self._query_api: Optional[QueryApi] = None
        
        self.connect()

    def connect(self) -> None:
        """Establish connection to InfluxDB server."""
        try:
            self._client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                enable_gzip=True
            )
            
            # Initialize write API with batching
            self._write_api = self._client.write_api(write_options=WriteOptions(
                batch_size=self.batch_size,
                flush_interval=self.flush_interval,
                jitter_interval=2_000,
                retry_interval=5_000,
                max_retries=5,
                max_retry_delay=30_000,
                exponential_base=2
            ))
            
            self._query_api = self._client.query_api()
            
            # Test connection
            self._client.ping()
            logger.info("Successfully connected to InfluxDB")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self.close()
            raise

    def close(self) -> None:
        """Close the client connection safely."""
        try:
            if self._write_api:
                self._write_api.close()
            if self._client:
                self._client.close()
        except Exception as e:
            logger.error(f"Error closing InfluxDB connection: {e}")
        finally:
            self._client = None
            self._write_api = None
            self._query_api = None

    @handle_influx_errors
    def write_measurement(
        self,
        measurement: str,
        fields: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
        bucket: Optional[str] = None
    ) -> None:
        """Write a measurement to InfluxDB."""
        point = Point(measurement)
        
        # Add fields
        for field_name, field_value in fields.items():
            point.field(field_name, field_value)
        
        # Add tags if provided
        if tags:
            for tag_name, tag_value in tags.items():
                point.tag(tag_name, tag_value)
        
        # Add timestamp if provided
        if timestamp:
            point.time(timestamp)
        
        self._write_api.write(
            bucket=bucket or self.default_bucket,
            org=self.org,
            record=point
        )

    @handle_influx_errors
    def write_batch(
        self,
        points: List[Point],
        bucket: Optional[str] = None
    ) -> None:
        """Write multiple points in a batch."""
        self._write_api.write(
            bucket=bucket or self.default_bucket,
            org=self.org,
            record=points
        )

    @handle_influx_errors
    def query_range(
        self,
        measurement: str,
        start: Union[datetime, timedelta],
        stop: Optional[datetime] = None,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        bucket: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query data within a time range with optional filters."""
        # Build Flux query
        query_parts = [
            f'from(bucket: "{bucket or self.default_bucket}")',
            f'|> range(start: {self._format_time(start)}',
        ]
        
        if stop:
            query_parts.append(f', stop: {self._format_time(stop)}')
        query_parts.append(')')
        
        # Add measurement filter
        query_parts.append(f'|> filter(fn: (r) => r["_measurement"] == "{measurement}")')
        
        # Add field filters if specified
        if fields:
            field_list = '", "'.join(fields)
            query_parts.append(f'|> filter(fn: (r) => contains(value: r["_field"], set: ["{field_list}"]))')
        
        # Add custom filters
        if filters:
            for key, value in filters.items():
                query_parts.append(f'|> filter(fn: (r) => r["{key}"] == "{value}")')
        
        query = ' '.join(query_parts)
        return self._query_api.query(query=query)

    @handle_influx_errors
    def delete_data(
        self,
        start: datetime,
        stop: datetime,
        measurement: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> None:
        """Delete data within a time range."""
        predicate = '_measurement="{}"'.format(measurement) if measurement else None
        
        self._client.delete_api().delete(
            start=start.isoformat() + 'Z',
            stop=stop.isoformat() + 'Z',
            predicate=predicate,
            bucket=bucket or self.default_bucket,
            org=self.org
        )

    def _format_time(self, time_value: Union[datetime, timedelta]) -> str:
        """Format time value for Flux query."""
        if isinstance(time_value, datetime):
            return time_value.isoformat() + 'Z'
        elif isinstance(time_value, timedelta):
            return f'-{int(time_value.total_seconds())}s'
        raise ValueError("Invalid time value type") 