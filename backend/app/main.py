from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import db
from routers import klines
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте подключаемся к БД
    await db.connect()
    yield
    # При выключении закрываем
    await db.close()

app = FastAPI(title="Crypto Screener API", lifespan=lifespan)

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

@app.get("/")
async def root():
    return {"status": "ok", "service": "Crypto Screener API v2"}
