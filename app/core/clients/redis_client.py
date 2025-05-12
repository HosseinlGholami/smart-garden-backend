import redis
import json
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    _instances = {}

    def __new__(cls, db=0):
        if db not in cls._instances:
            cls._instances[db] = super().__new__(cls)
            try:
                cls._instances[db]._redis_conn = redis.StrictRedis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=db,
                    decode_responses=True,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                cls._instances[db]._redis_conn.ping()
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._instances[db]

    def set_with_expiry(self, key: str, value: str, expiry_seconds: int) -> bool:
        """Set a key with expiry time."""
        try:
            return self._redis_conn.setex(key, expiry_seconds, value)
        except redis.RedisError as e:
            logger.error(f"Redis error in set_with_expiry: {e}")
            return False

    def get(self, key: str) -> str:
        """Get value for a key."""
        try:
            return self._redis_conn.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis error in get: {e}")
            return None

    def get_all_keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern."""
        try:
            return self._redis_conn.keys(pattern)
        except redis.RedisError as e:
            logger.error(f"Redis error in get_all_keys: {e}")
            return []

    def set_hash(self, key: str, field: str, value: dict) -> bool:
        """Set a hash field with JSON serialized value."""
        try:
            return self._redis_conn.hset(key, field, json.dumps(value))
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Redis error in set_hash: {e}")
            return False

    def get_hash(self, key: str) -> dict:
        """Get all fields and values in a hash."""
        try:
            return self._redis_conn.hgetall(key)
        except redis.RedisError as e:
            logger.error(f"Redis error in get_hash: {e}")
            return {}

    def get_dict(self, key: str) -> dict:
        """Get and deserialize a JSON value."""
        try:
            value = self._redis_conn.get(key)
            return json.loads(value) if value else None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis error in get_dict: {e}")
            return None

    def set_time(self, key: str) -> bool:
        """Set current timestamp for a key."""
        try:
            import time
            return self._redis_conn.set(key, str(time.time()))
        except redis.RedisError as e:
            logger.error(f"Redis error in set_time: {e}")
            return False

    def get_time(self, key: str) -> float:
        """Get timestamp for a key."""
        try:
            value = self._redis_conn.get(key)
            return float(value) if value else 0.0
        except (redis.RedisError, ValueError) as e:
            logger.error(f"Redis error in get_time: {e}")
            return 0.0

    def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            return bool(self._redis_conn.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis error in delete: {e}")
            return False

    def flush_db(self) -> bool:
        """Clear all keys in the current database."""
        try:
            return self._redis_conn.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis error in flush_db: {e}")
            return False 