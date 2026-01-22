from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import db
from routers import klines, screener, ws
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте подключаемся к БД
    await db.connect()
    
    # Запускаем мост Redis -> WebSocket
    redis_task = asyncio.create_task(ws.start_redis_listener())
    
    yield
    
    # При выключении закрываем задачу и соединения
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass
        
    await db.close()

app = FastAPI(title="Crypto Screener API", lifespan=lifespan)

# Gzip сжатие (минимум 1000 байт для сжатия)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS (разрешаем запросы с любого фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(klines.router, prefix="/api")
app.include_router(screener.router, prefix="/api")
app.include_router(ws.router) # Websocket at /ws

@app.get("/")
async def root():
    return {"status": "ok", "service": "Crypto Screener API v2"}
