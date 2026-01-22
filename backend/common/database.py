import os
import asyncpg
import redis.asyncio as redis
import logging

# Конфигурация из переменных окружения
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "timescaledb")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class DatabasePool:
    def __init__(self):
        self.pool = None
        self.redis = None

    async def connect(self):
        # PostgreSQL Connection
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=DATABASE_URL,
                    min_size=5,
                    max_size=20
                )
                print(f"✅ [Common] Connected to TimescaleDB at {DB_HOST}")
            except Exception as e:
                print(f"❌ [Common] Database connection failed: {e}")
                raise e
        
        # Redis Connection
        if not self.redis:
            try:
                self.redis = redis.Redis(
                    host=REDIS_HOST, 
                    port=6379, 
                    decode_responses=True
                )
                await self.redis.ping()
                print(f"✅ [Common] Connected to Redis at {REDIS_HOST}")
            except Exception as e:
                print(f"❌ [Common] Redis connection failed: {e}")
                self.redis = None

    async def close(self):
        if self.pool:
            await self.pool.close()
        if self.redis:
            await self.redis.close()
        print("🛑 [Common] Connections closed")

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

# Глобальный экземпляр
db = DatabasePool()
