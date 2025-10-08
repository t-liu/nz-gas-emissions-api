import redis
import json
import hashlib
from flask import current_app

# Initialize Redis connection
def init_redis_client():
    redis_config = {
        "host": current_app.config.get('REDIS_HOST', 'localhost'),
        "port": current_app.config.get('REDIS_PORT', 6379),
        "db": current_app.config.get('REDIS_DB', 0),
        "password": current_app.config.get('REDIS_PASSWORD', None)
    }

    try:
        redis_client = redis.Redis(**redis_config)
        redis_client.ping()
        print("Redis connection established successfully")
        return redis_client
    except redis.RedisError as err:
        print(f"Error connecting to Redis: {err}")
        return None

# Global Redis client
redis_client = None

# Cache settings
CACHE_TTL = 300  # 5 minutes for successful responses

def generate_cache_key(endpoint, params):
    """Generate a unique cache key based on endpoint and query parameters."""
    sorted_params = sorted(params.items())
    param_str = json.dumps(sorted_params, sort_keys=True)
    return f"{endpoint}:{hashlib.md5(param_str.encode('utf-8')).hexdigest()}"

def get_cached_response(endpoint, params):
    """Retrieve cached response from Redis."""
    global redis_client
    if redis_client is None:
        redis_client = init_redis_client()

    if redis_client:
        try:
            cache_key = generate_cache_key(endpoint, params)
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except redis.RedisError as err:
            print(f"Redis error: {err}")
    return None

def cache_response(endpoint, params, response, ttl=CACHE_TTL):
    """Cache response in Redis with specified TTL."""
    global redis_client
    if redis_client is None:
        redis_client = init_redis_client()

    if redis_client:
        try:
            cache_key = generate_cache_key(endpoint, params)
            redis_client.setex(cache_key, ttl, json.dumps(response))
        except redis.RedisError as err:
            print(f"Redis error while caching: {err}")