import redis
import json
from datetime import timedelta
import os
import time

class RedisClient:
    _instances = {}

    def __new__(cls, db=0):
        if db not in cls._instances:
            cls._instances[db] = super().__new__(cls)
            cls._instances[db]._redis_conn = redis.StrictRedis(
                host=os.environ['LOCAL_IP'], port=6379, db=db)
        return cls._instances[db]

    # used for camera data :
    def set_with_expiry(self, key, value, expiry_seconds):
        self._redis_conn.setex(key.encode(), expiry_seconds, value.encode())

    def get(self, key):
        value = self._redis_conn.get(key.encode())
        if value:
            return value.decode()
        return None

    def get_all_keys(self):
        return [key.decode() for key in self._redis_conn.keys()]

    # used for sorter event and api's
    def set_hash(self, key, field, value):
        self._redis_conn.hset(key, field, json.dumps(value))

    def get_hash(self, key):
        hash_data = self._redis_conn.hgetall(key)
        result = {}
        for field, value in hash_data.items():
            result[field.decode()] = value.decode()
        return result

    def get_dict(self, key):
        value = self._redis_conn.get(key)
        if value:
            return json.loads(value)
        return None

# used for camera timestamp for embededd debuging 
    def set_time(self, key):
        self._redis_conn.set(key.encode(), time.time())
    def get_time(self, key ):
        return float(self._redis_conn.get(key.encode()))