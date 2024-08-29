#!/usr/bin/env python3
"""
A module that provides a caching mechanism using Redis,
with method call counting and history tracking.
"""
import redis
import uuid
from typing import Union, Callable, Optional
import functools


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of times a method is called.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to increment the call count and call the
        original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the history of inputs and outputs of a method.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store the history of inputs and outputs.
        """
        # Generate keys for inputs and outputs
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(inputs_key, str(args))
        
        # Call the original method and get the result
        result = method(self, *args, **kwargs)
        
        # Store the result
        self._redis.rpush(outputs_key, result)
        
        return result

    return wrapper


class Cache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize the Cache instance, set up the Redis client,
        and flush the database.
        """
        self._redis = redis.Redis(host=host, port=port, db=db)
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the data in Redis with a randomly generated key
        and return the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a
        conversion function `fn`.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis.
        """
        return self.get(key, lambda d: int(d))
