import asyncio
import ccxt.async_support as ccxt
from datetime import datetime, timedelta, timezone
from common.database import db

async def fetch_and_save(exchange, symbol, since):
    try:
        # 1. Загружаем 24 часа данных
        candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1440)
        if not candles:
            return 0
        
        # 2. Подготавливаем записи
        records = []
        for c in candles:
            dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
            records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
        
        # 3. Сохраняем в БД (пакетная вставка)
        query = """
            INSERT INTO candles (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO UPDATE SET
                open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close;
        """
        async with db.pool.acquire() as conn:
            await conn.executemany(query, records)
        return len(candles)
    except Exception as e:
        print(f"  [!] Error {symbol}: {e}")
        return 0

async def sync_all_fast():
    print("🚀 Starting FAST FORCE 24H SYNC (Parallel Mode)...")
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
        
        # Обрабатываем пачками по 10 монет параллельно
        batch_size = 10
        total_synced = 0
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            tasks = [fetch_and_save(exchange, symbol, since) for symbol in batch]
            
            results = await asyncio.gather(*tasks)
            total_synced += sum(results)
            
            progress = min(i + batch_size, len(symbols))
            print(f"  [+] Progress: {progress}/{len(symbols)} symbols. Total candles: {total_synced}")
            
            # Небольшая пауза для стабильности
            await asyncio.sleep(0.5)
            
    finally:
        await exchange.close()
        await db.close()
        print("✅ FAST SYNC FINISHED.")

if __name__ == "__main__":
    asyncio.run(sync_all_fast())
