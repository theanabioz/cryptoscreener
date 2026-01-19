import ccxt.async_support as ccxt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.services.market_data import market_manager
from app.services.technical_analysis import ta_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ws_task = asyncio.create_task(market_manager.start_stream())
    ta_task = asyncio.create_task(ta_service.start_loop())
    yield
    # Shutdown
    market_manager.running = False
    ta_service.running = False
    ws_task.cancel()
    ta_task.cancel()
    await ta_service.close()

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

@app.get("/api/klines/{symbol}")
async def get_klines(symbol: str, interval: str = '1h', limit: int = 500):
    exchange = ccxt.binance()
    try:
        # Приводим символ к формату Binance (BTCUSDT)
        formatted_symbol = symbol.upper()
        if not formatted_symbol.endswith('USDT'):
            formatted_symbol += 'USDT'
            
        ohlcv = await exchange.fetch_ohlcv(formatted_symbol, timeframe=interval, limit=limit)
        
        # Форматируем для Lightweight Charts: { time: 1234567890, open: ..., high: ..., low: ..., close: ... }
        formatted_data = []
        for candle in ohlcv:
            formatted_data.append({
                "time": int(candle[0] / 1000), # Unix timestamp in seconds
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5]
            })
            
        return formatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await exchange.close()

@app.get("/api/coins")
async def get_coins(limit: int = 400):
    tickers = market_manager.get_all_tickers()
    
    result = []
    # Теперь отдаем до 400 монет
    for t in tickers[:limit]:
        result.append({
            "id": t['symbol'].replace('USDT', '').lower(),
            "symbol": t['symbol'].replace('USDT', ''),
            "name": t['symbol'].replace('USDT', ''), 
            "current_price": t['price'],
            "price_change_percentage_24h": t['change_24h'],
            "market_cap": 0, 
            "total_volume": t['volume'],
            # Новые поля TA
            "rsi": t.get('rsi'),
            "macd": t.get('macd'),
            "ema50": t.get('ema50'),
            "bb_pos": t.get('bb_pos'),
            "trend": t.get('trend'),
            "image": f"https://assets.coincap.io/assets/icons/{t['symbol'].replace('USDT', '').lower()}@2x.png"
        })
    return result

@app.get("/health")
def health():
    return {"status": "running_v3_ta", "tickers_count": len(market_manager.prices)}

