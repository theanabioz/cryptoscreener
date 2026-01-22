from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import db
from routers import klines, screener
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте подключаемся к БД
    await db.connect()
    yield
    # При выключении закрываем
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

@app.get("/")
async def root():
    return {"status": "ok", "service": "Crypto Screener API v2"}
