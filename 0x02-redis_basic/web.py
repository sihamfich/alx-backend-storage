#!/usr/bin/env python3
"""
A module to fetch and cache web pages using Redis.
"""
import redis
import requests
from functools import wraps
from typing import Callable

# Configure Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

def cache_page(func: Callable) -> Callable:
    """
    A decorator that caches the result of a function and tracks the number of accesses.
    """
    @wraps(func)
    def wrapper(url: str, *args, **kwargs):
        # Create Redis client
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        
        # Redis key for cached content
        cache_key = f"page_cache:{url}"
        # Redis key for access count
        access_count_key = f"page_access_count:{url}"

        # Check if the URL is in the cache
        cached_content = redis_client.get(cache_key)
        if cached_content:
            redis_client.incr(access_count_key)  # Increment the access count
            print(f"Cache hit for {url}")
            return cached_content.decode('utf-8')  # Return the cached content

        # Fetch the content if not cached
        print(f"Cache miss for {url}. Fetching from the web...")
        page_content = func(url, *args, **kwargs)
        
        # Store the content in the cache with an expiration of 10 seconds
        redis_client.setex(cache_key, 10, page_content)
        redis_client.incr(access_count_key)  # Increment the access count

        return page_content

    return wrapper

@cache_page
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text
