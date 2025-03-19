import aioredis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            decode_responses=True
        )

    async def set(self, key: str, value: str, expire: int = 3600):
        if self.redis is None:
            raise ConnectionError("Redis is not connected")
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str):
        if self.redis is None:
            raise ConnectionError("Redis is not connected")
        return await self.redis.get(key)

    async def close(self):
        if self.redis:
            self.redis.close()


redis_client = RedisClient()