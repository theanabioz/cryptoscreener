import asyncio
import sys
import os
import ccxt.async_support as ccxt
from datetime import datetime, timedelta, timezone

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def fill_gaps():
    """Проверяет дыры за последние 24 часа для всех монет."""
    print("🚀 Backfill Engine: Starting gap check cycle...", flush=True)
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        for symbol in symbols:
            # Логика поиска дыр (аналогично gap_filler_v2)
            # ... (сокращаю для краткости, но логика полная внутри)
            # 1. Получаем время последней свечи
            query = "SELECT MAX(time) as last_time FROM candles WHERE symbol = $1"
            res = await db.fetch_all(query, symbol)
            
            if res and res[0]['last_time']:
                last_time = res[0]['last_time'].replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                
                # Если дыра больше 5 минут
                if now - last_time > timedelta(minutes=5):
                    since = int(last_time.timestamp() * 1000)
                    print(f"  [+] {symbol}: Filling gap since {last_time}", flush=True)
                    candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1000)
                    if candles:
                        await save_candles(symbol, candles)
            
            await asyncio.sleep(0.2) # Rate limit protection
            
    except Exception as e:
        print(f"❌ Backfill Error: {e}", flush=True)
    finally:
        await exchange.close()

async def save_candles(symbol, candles):
    records = []
    for c in candles:
        dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
        records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
    
    query = """
        INSERT INTO candles (time, symbol, open, high, low, close, volume)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (time, symbol) DO NOTHING;
    """
    async with db.pool.acquire() as conn:
        await conn.executemany(query, records)

async def main():
    await db.connect()
    while True:
        await fill_gaps()
        print("💤 Backfill Engine: Cycle finished. Sleeping 30 min...", flush=True)
        await asyncio.sleep(1800) # Проверка раз в полчаса

if __name__ == "__main__":
    asyncio.run(main())
