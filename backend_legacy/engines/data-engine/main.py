import asyncio
import sys
import os
import json
import ccxt.pro as ccxt_pro
from datetime import datetime

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_streamer():
    """Слушает живые котировки Binance и пушит ТОЛЬКО в Redis."""
    print("🚀 Data Engine: Real-time Price Streamer started (No-DB mode)", flush=True)
    
    exchange = ccxt_pro.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    while True:
        try:
            tickers = await exchange.watch_tickers()
            if tickers:
                for symbol, ticker in tickers.items():
                    if not symbol.endswith('/USDT'): continue
                    
                    timestamp = ticker['timestamp'] or int(datetime.now().timestamp() * 1000)
                    current_price = ticker['last']
                    
                    # Формируем легкий пакет для фронтенда
                    # s: symbol, k: [t, o, h, l, c, v]
                    # Используем last для всех полей OHLC, чтобы не брать 24h open
                    candle = [timestamp, current_price, current_price, current_price, current_price, ticker['baseVolume']]

                    if db.redis:
                        await db.redis.publish("crypto_updates", json.dumps({"s": symbol, "k": candle}))
                        
        except Exception as e:
            print(f"❌ Streamer Error: {e}", flush=True)
            await asyncio.sleep(5)

async def main():
    await db.connect()
    await run_streamer()

if __name__ == "__main__":
    asyncio.run(main())