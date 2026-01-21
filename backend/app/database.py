import os
import asyncpg
from contextlib import asynccontextmanager

# Читаем настройки из переменных окружения или ставим дефолт (для Docker внутри сети)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "timescaledb")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "screener")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class DatabasePool:
    def __init__(self):
        self.pool = None

    async def connect(self):
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

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("🛑 Database connection closed")

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

db = DatabasePool()
