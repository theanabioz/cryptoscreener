from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Crypto Screener API",
    description="Backend for Telegram Mini App using TVScreener",
    version="1.0.0"
)

# CORS (чтобы фронтенд мог слать запросы)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Crypto Screener Backend"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
