import os
import asyncpg
import redis.asyncio as redis
import logging

class Database:
    def __init__(self):
        self.pool = None
        self.redis = None
        self.logger = logging.getLogger("Database")

    async def connect(self):
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        db_name = os.getenv("POSTGRES_DB", "postgres")
        host = os.getenv("POSTGRES_HOST", "timescaledb")
        port = os.getenv("POSTGRES_PORT", "5432")
        
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        
        try:
            self.pool = await asyncpg.create_pool(dsn=dsn, min_size=5, max_size=20)
            print("✅ [Common] Connected to PostgreSQL")
        except Exception as e:
            print(f"❌ [Common] DB Connection failed: {e}")
            raise e

        try:
            redis_host = os.getenv("REDIS_HOST", "redis")
            self.redis = redis.Redis(host=redis_host, port=6379, decode_responses=True)
            await self.redis.ping()
            print("✅ [Common] Connected to Redis")
        except Exception as e:
            print(f"❌ [Common] Redis Connection failed: {e}")
            self.redis = None

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

db = Database()
