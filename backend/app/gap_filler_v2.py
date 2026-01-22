import asyncio
import ccxt.pro as ccxt_pro
import ccxt
import logging
import pandas as pd
from datetime import datetime, timedelta, timezone
from database import db
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fill_symbol_gaps(exchange, symbol):
    """
    Ищет и заполняет дыры в минутных свечах за последние 24 часа для конкретного символа.
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
        
        if not rows:
            logger.info(f"[{symbol}] No data in DB for last 24h. Skipping.")
            return

        existing_times = {r['time'].replace(tzinfo=timezone.utc).timestamp() for r in rows}
        
        # 2. Генерируем эталонный список (каждая минута)
        # От первой до последней записи в базе
        first_db_time = rows[0]['time'].replace(tzinfo=timezone.utc)
        last_db_time = rows[-1]['time'].replace(tzinfo=timezone.utc)
        
        expected_time = first_db_time
        gaps = []
        
        while expected_time <= last_db_time:
            ts = expected_time.timestamp()
            if ts not in existing_times:
                # Нашли начало дыры
                gap_start = expected_time
                # Ищем конец дыры
                while expected_time <= last_db_time and expected_time.timestamp() not in existing_times:
                    expected_time += timedelta(minutes=1)
                gap_end = expected_time
                gaps.append((gap_start, gap_end))
            
            expected_time += timedelta(minutes=1)

        if not gaps:
            return

        logger.info(f"[{symbol}] Found {len(gaps)} gaps. Filling...")

        # 3. Докачиваем данные из Binance
        for gap_start, gap_end in gaps:
            # fetch_ohlcv в CCXT принимает timestamp в мс
            since = int(gap_start.timestamp() * 1000)
            # Ограничиваем количество свечей (Binance дает до 1000 за раз)
            limit = min(int((gap_end - gap_start).total_seconds() / 60) + 1, 1000)
            
            if limit <= 0: continue

            candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=limit)
            
            if not candles:
                continue

            records = []
            for c in candles:
                dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                # (time, symbol, open, high, low, close, volume)
                records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))

            if records:
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
                
                logger.info(f"[{symbol}] Injected {len(records)} missing candles.")

    except Exception as e:
        logger.error(f"Error filling gaps for {symbol}: {e}")

async def main():
    logger.info("🚀 Starting Advanced Gap Filler v2...")
    await db.connect()
    
    # Используем обычный CCXT для докачки истории (не Pro)
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Получаем список монет из мета-данных
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        if not symbols:
            logger.warning("No symbols found. Checking candles table...")
            rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles WHERE time > NOW() - INTERVAL '2 days'")
            symbols = [r['symbol'] for r in rows]

        logger.info(f"Checking {len(symbols)} symbols...")
        
        # Обрабатываем последовательно, чтобы не спамить Binance
        for i, symbol in enumerate(symbols):
            if (i+1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(symbols)}")
            await fill_symbol_gaps(exchange, symbol)
            
    finally:
        await exchange.close()
        await db.close()
        logger.info("✅ Gap Filler finished.")

if __name__ == "__main__":
    asyncio.run(main())
