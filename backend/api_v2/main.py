from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import sys
import os

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db
from api_v2.routers import klines, screener, ws

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 API v2: Starting lifespan", flush=True)
    await db.connect()
    # Запускаем мост Redis -> WebSocket
    redis_task = asyncio.create_task(ws.start_redis_listener())
    yield
    redis_task.cancel()
    await db.close()
    print("🛑 API v2: Lifespan closed", flush=True)

app = FastAPI(title="Crypto Screener API v2", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(klines.router, prefix="/api")
app.include_router(screener.router, prefix="/api")
app.include_router(ws.router)

@app.get("/")
async def root():
    return {"status": "ok", "version": "2.0", "architecture": "distributed-engines"}
