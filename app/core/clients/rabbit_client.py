"""
RabbitMQ client for message queue operations.
Provides a robust interface for publishing and consuming messages with proper connection management.
"""

import pika
import struct
import time
from typing import Any, Callable, Dict, Optional, Union
from django.conf import settings
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def ensure_connection(func):
    """Decorator to ensure connection is active before executing a method."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            if not self.is_connected():
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            return func(self, *args, **kwargs)
        except (pika.exceptions.AMQPError, pika.exceptions.ChannelError) as e:
            logger.error(f"RabbitMQ operation failed: {e}")
            self.close()
            raise
    return wrapper

class RabbitMQClient:
    """Client for interacting with RabbitMQ message broker."""
    
    def __init__(
        self,
        host: str = settings.RABBITMQ_HOST,
        port: int = settings.RABBITMQ_PORT,
        virtual_host: str = settings.RABBITMQ_VHOST,
        username: str = settings.RABBITMQ_USER,
        password: str = settings.RABBITMQ_PASSWORD,
        connection_attempts: int = 3,
        retry_delay: int = 5
    ):
        """Initialize RabbitMQ client with connection parameters."""
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password),
            connection_attempts=connection_attempts,
            retry_delay=retry_delay,
            heartbeat=600
        )
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self.connect()

    def connect(self) -> None:
        """Establish connection to RabbitMQ server."""
        try:
            if not self.is_connected():
                self._connection = pika.BlockingConnection(self.connection_params)
                self._channel = self._connection.channel()
                logger.info("Successfully connected to RabbitMQ")
        except pika.exceptions.AMQPError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def is_connected(self) -> bool:
        """Check if connection is active and healthy."""
        return (
            self._connection is not None and 
            not self._connection.is_closed and
            self._channel is not None and 
            not self._channel.is_closed
        )

    def close(self) -> None:
        """Close the connection and channel safely."""
        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
            if self._connection and not self._connection.is_closed:
                self._connection.close()
        except pika.exceptions.AMQPError as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
        finally:
            self._channel = None
            self._connection = None

    @ensure_connection
    def send_message(self, routing_key: str, data: Dict[str, Any]) -> None:
        """Send a message to RabbitMQ with the specified routing key."""
        try:
            message = self._pack_message(data)
            self._channel.basic_publish(
                exchange="amq.topic",
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            logger.debug(f"Message sent to routing_key: {routing_key}")
        except (struct.error, TypeError) as e:
            logger.error(f"Error packing message: {e}")
            raise
        except pika.exceptions.AMQPError as e:
            logger.error(f"Error publishing message: {e}")
            raise

    def _pack_message(self, data: Dict[str, Any]) -> bytes:
        """Pack message data into binary format."""
        try:
            return struct.pack(
                '<BqBBi',
                data["version"],
                data["timestamp"],
                data["type"],
                data["address"],
                data["data"]
            )
        except (KeyError, struct.error) as e:
            logger.error(f"Error packing message: {e}")
            raise

    def parse_message(self, body: bytes) -> Dict[str, Any]:
        """Parse binary message into dictionary format."""
        try:
            data = struct.unpack('<BqBBi', body)
            return {
                "version": data[0],
                "timestamp": data[1],
                "type": data[2],
                "address": data[3],
                "data": data[4]
            }
        except struct.error as e:
            logger.error(f"Error parsing message: {e}")
            raise

    @ensure_connection
    def publish_and_listen(
        self,
        send_routing_key: str,
        listen_routing_key: str,
        data: Dict[str, Any],
        queue_name: str,
        timeout: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Publish a message and wait for response on a temporary queue."""
        try:
            # Declare queue and bind it
            self._channel.queue_declare(queue=queue_name, auto_delete=True)
            self._channel.queue_bind(
                exchange="amq.topic",
                queue=queue_name,
                routing_key=listen_routing_key
            )

            response = {"received": False, "data": None}

            def on_response(ch, method, props, body):
                response["received"] = True
                response["data"] = self.parse_message(body)

            # Set up consumer
            self._channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_response,
                auto_ack=True
            )

            # Send message
            self.send_message(send_routing_key, data)

            # Wait for response with timeout
            start_time = time.time()
            while not response["received"] and (time.time() - start_time) < timeout:
                self._connection.process_data_events(time_limit=0.5)

            return response["data"]
        finally:
            # Clean up
            try:
                self._channel.queue_delete(queue=queue_name)
            except pika.exceptions.AMQPError as e:
                logger.error(f"Error cleaning up temporary queue: {e}")

    @ensure_connection
    def listen_for_messages(
        self,
        queue_name: str,
        routing_key: str,
        callback: Callable,
        durable: bool = True
    ) -> None:
        """Set up a consumer to listen for messages on a queue."""
        try:
            self._channel.queue_declare(queue=queue_name, durable=durable)
            self._channel.queue_bind(
                exchange="amq.topic",
                queue=queue_name,
                routing_key=routing_key
            )
            self._channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            logger.info(f"Started consuming from queue: {queue_name}")
            self._channel.start_consuming()
        except pika.exceptions.AMQPError as e:
            logger.error(f"Error in message consumer: {e}")
            raise 