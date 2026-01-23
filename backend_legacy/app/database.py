import os
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Читаем настройки из переменных окружения или ставим дефолт (для Docker внутри сети)
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
                print(f"✅ Connected to TimescaleDB at {DB_HOST}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise e
        
        # Redis Connection
        if not self.redis:
            try:
                r = redis.Redis(
                    host=REDIS_HOST, 
                    port=6379, 
                    decode_responses=True
                )
                await r.ping()
                self.redis = r
                print(f"✅ Connected to Redis at {REDIS_HOST}")
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
                self.redis = None # Явно сбрасываем


    async def close(self):
        if self.pool:
            await self.pool.close()
            print("🛑 Database connection closed")
        
        if self.redis:
            await self.redis.close()
            print("🛑 Redis connection closed")

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

db = DatabasePool()
