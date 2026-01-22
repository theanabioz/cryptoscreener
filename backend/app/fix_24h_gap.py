import asyncio
import ccxt.async_support as ccxt
from datetime import datetime, timedelta, timezone
from common.database import db

async def fix_gap():
    await db.connect()
    exchange = ccxt.binance({'enableRateLimit': True})
    
    rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
    symbols = [r['symbol'] for r in rows]
    
    since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000)
    
    print(f"🚀 Filling 24h gap for {len(symbols)} symbols...")
    
    for i, symbol in enumerate(symbols):
        try:
            candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1440)
            if candles:
                records = []
                for c in candles:
                    dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                    records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
                
                query = """
                    INSERT INTO candles (time, symbol, open, high, low, close, volume)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (time, symbol) DO UPDATE SET
                        open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close;
                """
                async with db.pool.acquire() as conn:
                    await conn.executemany(query, records)
                print(f"[{i+1}/{len(symbols)}] {symbol}: {len(candles)} candles added")
        except Exception as e:
            print(f"Error {symbol}: {e}")
        await asyncio.sleep(0.1)

    await exchange.close()
    await db.close()

if __name__ == "__main__":
    asyncio.run(fix_gap())
