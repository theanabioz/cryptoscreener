from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.services.market_data import market_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Binance Stream
    task = asyncio.create_task(market_manager.start_stream())
    yield
    # Shutdown
    market_manager.running = False
    task.cancel()

app = FastAPI(
    title="Crypto Screener Core",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/coins")
async def get_coins(limit: int = 50):
    tickers = market_manager.get_all_tickers()
    
    result = []
    for t in tickers[:limit]:
        result.append({
            "id": t['symbol'].replace('USDT', '').lower(),
            "symbol": t['symbol'].replace('USDT', ''),
            "name": t['symbol'].replace('USDT', ''), 
            "current_price": t['price'],
            "price_change_percentage_24h": t['change_24h'],
            "market_cap": 0, 
            "total_volume": t['volume'],
            "image": f"https://assets.coincap.io/assets/icons/{t['symbol'].replace('USDT', '').lower()}@2x.png"
        })
    return result

@app.get("/health")
def health():
    return {"status": "running", "tickers_count": len(market_manager.prices)}