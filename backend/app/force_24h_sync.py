import asyncio
import ccxt.async_support as ccxt
from datetime import datetime, timedelta, timezone
from common.database import db

async def sync_all():
    print("🚀 Starting FORCE 24H SYNC for all active symbols...")
    await db.connect()
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        now = datetime.now(timezone.utc)
        since = int((now - timedelta(hours=24)).timestamp() * 1000)
        
        print(f"Targeting {len(symbols)} symbols. Since: {now - timedelta(hours=24)}")
        
        for i, symbol in enumerate(symbols):
            try:
                # 1. Загружаем 24 часа данных (1440 минут)
                candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1440)
                if not candles:
                    print(f"  [-] {symbol}: No data found on Binance.")
                    continue
                
                # 2. Подготавливаем записи
                records = []
                for c in candles:
                    dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                    records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
                
                # 3. Сохраняем в БД
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
                
                if (i + 1) % 10 == 0 or symbol == 'SOL/USDT':
                    print(f"  [+] ({i+1}/{len(symbols)}) {symbol}: {len(candles)} candles synced.")
                    
            except Exception as e:
                print(f"  [!] Error {symbol}: {e}")
            
            # Небольшая пауза для лимитов
            await asyncio.sleep(0.1)
            
    finally:
        await exchange.close()
        await db.close()
        print("✅ FORCE SYNC FINISHED.")

if __name__ == "__main__":
    asyncio.run(sync_all())
