import time
import redis
from flask import current_app

r = None

def init_redis(app):
    global r
    r = redis.Redis.from_url(app.config["REDIS_URL"], decode_responses=True)

def is_rate_limited(api_key: str, service: str) -> bool:
    now = int(time.time())
    window = now // current_app.config["RATE_PERIOD"]
    limit = current_app.config["RATE_LIMITS"].get(f"/{service}", 100)

    key = f"rate:{api_key}:{service}:{window}"
    count = r.incr(key)

    if count == 1:
        r.expire(key, current_app.config["RATE_PERIOD"])

    return count > limit
