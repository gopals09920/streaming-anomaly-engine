import fakeredis.aioredis as redis

# In-memory Redis server for local execution without Docker
redis_client = redis.FakeRedis(decode_responses=True)

async def update_and_get_velocity(user_id: str) -> int:
    """Sliding-window transaction count increment over short TTL."""
    key = f"user:{user_id}:velocity"
    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, 300)  # 5 minutes window
        res = await pipe.execute()
    return res[0]