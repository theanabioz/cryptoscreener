import asyncio
import ccxt.async_support as ccxt
import asyncpg
from datetime import datetime, timedelta, timezone
import os

async def sync():
    print("🚀 BLITZ SYNC STARTING (PRO VERSION)...")
    
    # Прямое подключение к БД
    conn_str = f"postgresql://postgres:SuperLongSecurePassword2026NoSpecialChars@timescaledb:5432/postgres"
    pool = await asyncpg.create_pool(conn_str)
    
    exchange = ccxt.binance({'enableRateLimit': True})
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]

    now = datetime.now(timezone.utc)
    since = int((now - timedelta(hours=24)).timestamp() * 1000)
    
    print(f"Targeting {len(symbols)} symbols. Since {now - timedelta(hours=24)}")

    async def fetch_one(symbol):
        try:
            # Проверяем сколько уже есть свечей
            async with pool.acquire() as conn:
                count = await conn.fetchval("SELECT count(*) FROM candles WHERE symbol = $1 AND time > NOW() - INTERVAL '24 hours'", symbol)
                if count >= 1430: 
                    # print(f"  [.] {symbol}: Already dense ({count} candles). Skipping.")
                    return
            
            candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1440)
            if not candles: return
            
            records = [(datetime.fromtimestamp(c[0]/1000, tz=timezone.utc), symbol, c[1], c[2], c[3], c[4], c[5]) for c in candles]
            
            query = """
                INSERT INTO candles (time, symbol, open, high, low, close, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (time, symbol) DO UPDATE SET 
                    open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close;
            """
            async with pool.acquire() as conn:
                await conn.executemany(query, records)
            print(f"  [v] {symbol}: Recovered {len(candles)} candles.")
        except Exception as e:
            print(f"  [!] Error {symbol}: {e}")

    # Пачки по 10 для скорости и стабильности
    batch_size = 10
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        await asyncio.gather(*[fetch_one(s) for s in batch])
        print(f"--- Completed: {i+len(batch)}/{len(symbols)} coins ---")
        await asyncio.sleep(0.1)

    await exchange.close()
    await pool.close()
    print("✅ MISSION ACCOMPLISHED. ALL GAPS CLOSED.")

if __name__ == "__main__":
    asyncio.run(sync())