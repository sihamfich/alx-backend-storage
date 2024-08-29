#!/usr/bin/env python3
"""
A module that provides a caching mechanism using Redis.
"""
import redis
import uuid
from typing import Union

class Cache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize the Cache instance, set up the Redis client, and flush the database.
        """
        self._redis = redis.Redis(host=host, port=port, db=db)
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the data in Redis with a randomly generated key and return the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

