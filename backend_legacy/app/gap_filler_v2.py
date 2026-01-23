import asyncio
import ccxt.async_support as ccxt
import logging
from datetime import datetime, timedelta, timezone
from database import db
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fill_symbol_gaps(exchange, symbol):
    """
    Ищет и заполняет дыры в минутных свечах за последние 24 часа.
    """
    try:
        # 1. Получаем все свечи из БД за последние 24 часа
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        query = """
            SELECT time FROM candles 
            WHERE symbol = $1 AND time > $2
            ORDER BY time ASC
        """
        rows = await db.fetch_all(query, symbol, start_time)
        
        if not rows or len(rows) < 2:
            # Если данных совсем мало, попробуем просто скачать последние 500 свечей
            logger.info(f"[{symbol}] Minimal data in DB. Fetching last 500 candles.")
            candles = await exchange.fetch_ohlcv(symbol, '1m', limit=500)
            await save_candles(symbol, candles)
            return

        existing_times = {r['time'].replace(tzinfo=timezone.utc).timestamp() for r in rows}
        
        # 2. Поиск дыр
        first_db_time = rows[0]['time'].replace(tzinfo=timezone.utc)
        last_db_time = rows[-1]['time'].replace(tzinfo=timezone.utc)
        
        expected_time = first_db_time
        while expected_time <= last_db_time:
            ts = expected_time.timestamp()
            if ts not in existing_times:
                gap_start = expected_time
                # Нашли начало дыры, ищем конец (до 1000 минут)
                count = 0
                while expected_time <= last_db_time and expected_time.timestamp() not in existing_times and count < 1000:
                    expected_time += timedelta(minutes=1)
                    count += 1
                
                gap_end = expected_time
                logger.info(f"[{symbol}] Filling gap: {gap_start} -> {gap_end} ({count} min)")
                
                since = int(gap_start.timestamp() * 1000)
                candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=count)
                if candles:
                    await save_candles(symbol, candles)
            
            expected_time += timedelta(minutes=1)

    except Exception as e:
        logger.error(f"Error filling gaps for {symbol}: {e}")

async def save_candles(symbol, candles):
    if not candles: return
    records = []
    for c in candles:
        dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
        records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
    
    query_insert = """
        INSERT INTO candles (time, symbol, open, high, low, close, volume)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (time, symbol) DO UPDATE SET
            high = GREATEST(candles.high, EXCLUDED.high),
            low = LEAST(candles.low, EXCLUDED.low),
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """
    async with db.pool.acquire() as conn:
        await conn.executemany(query_insert, records)

async def main():
    logger.info("🚀 Starting Advanced Gap Filler v2 (Async)...")
    await db.connect()
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        if not symbols:
            rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles WHERE time > NOW() - INTERVAL '2 days'")
            symbols = [r['symbol'] for r in rows]

        logger.info(f"Checking {len(symbols)} symbols...")
        
        for i, symbol in enumerate(symbols):
            if (i+1) % 20 == 0:
                logger.info(f"Progress: {i+1}/{len(symbols)}")
            await fill_symbol_gaps(exchange, symbol)
            # Небольшая пауза чтобы не триггерить rate limit сильно
            await asyncio.sleep(0.1)
            
    finally:
        await exchange.close()
        await db.close()
        logger.info("✅ Gap Filler finished.")

if __name__ == "__main__":
    asyncio.run(main())