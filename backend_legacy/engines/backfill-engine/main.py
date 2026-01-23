import asyncio
import sys
import os
import ccxt.async_support as ccxt
from datetime import datetime, timedelta, timezone
from common.database import db

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def sync_candles():
    """Синхронизирует последние минутные свечи для всех активных монет."""
    print(f"🔄 Syncing candles at {datetime.now()}", flush=True)
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        # Обрабатываем пачками по 5 символов параллельно для скорости
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            tasks = [fetch_and_save(exchange, s) for s in batch]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1) # Лимиты API
            
    except Exception as e:
        print(f"❌ Sync Error: {e}", flush=True)
    finally:
        await exchange.close()

async def fetch_and_save(exchange, symbol):
    try:
        # Берем последние 5 свечей (запас на случай лагов)
        candles = await exchange.fetch_ohlcv(symbol, '1m', limit=5)
        if not candles: return
        
        records = []
        for c in candles:
            dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
            records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
        
        query = """
            INSERT INTO candles (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
        """
        async with db.pool.acquire() as conn:
            await conn.executemany(query, records)
    except Exception as e:
        print(f"  [!] Error {symbol}: {e}")

async def main():
    await db.connect()
    while True:
        start_time = datetime.now()
        await sync_candles()
        elapsed = (datetime.now() - start_time).total_seconds()
        # Цикл раз в минуту
        wait_time = max(60 - elapsed, 10)
        print(f"💤 Sync finished in {elapsed:.1f}s. Waiting {wait_time:.1f}s...")
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    asyncio.run(main())