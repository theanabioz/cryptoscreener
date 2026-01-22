import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import logging
from datetime import datetime, timezone
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fill_gap_for_symbol(exchange, symbol):
    try:
        # 1. Узнаем время последней свечи в базе
        query = "SELECT max(time) as last_time FROM candles WHERE symbol = $1"
        row = await db.fetch_all(query, symbol)
        
        last_time = row[0]['last_time'] if row and row[0]['last_time'] else None
        
        if not last_time:
            logger.warning(f"No data for {symbol} in DB. Skipping.")
            return

        # Binance использует миллисекунды. 
        # Добавляем 1 минуту к последней свече, чтобы не качать дубликат
        since = int(last_time.timestamp() * 1000) + 60000
        now = int(datetime.now(timezone.utc).timestamp() * 1000)

        if since >= now - 60000:
            logger.info(f"✅ {symbol} is already up to date.")
            return

        logger.info(f"⏳ {symbol}: Gap from {last_time} to now. Fetching...")

        all_candles = []
        current_since = since
        
        while current_since < now:
            candles = await exchange.fetch_ohlcv(symbol, timeframe='1m', since=current_since, limit=1000)
            if not candles:
                break
            
            all_candles.extend(candles)
            current_since = candles[-1][0] + 60000
            
            if len(candles) < 1000: # Больше данных нет
                break
                
            await asyncio.sleep(0.1) # Rate limit protection

        if not all_candles:
            return

        # 2. Массовая вставка в БД
        # Превращаем в кортежи для asyncpg executemany
        records = [
            (datetime.fromtimestamp(c[0]/1000, tz=timezone.utc), symbol, c[1], c[2], c[3], c[4], c[5])
            for c in all_candles
        ]

        insert_query = """
            INSERT INTO candles (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO NOTHING
        """
        
        async with db.pool.acquire() as conn:
            await conn.executemany(insert_query, records)

        logger.info(f"🚀 {symbol}: Inserted {len(all_candles)} new candles.")

    except Exception as e:
        logger.error(f"Error filling gap for {symbol}: {e}")

async def main():
    logger.info("Starting Gap Filler...")
    await db.connect()
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    try:
        # Получаем список всех символов из базы
        symbols_rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles")
        symbols = [r['symbol'] for r in symbols_rows]
        
        logger.info(f"Found {len(symbols)} symbols to check.")
        
        # Обрабатываем пачками по 5 для скорости, но не превышая лимиты
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            tasks = [fill_gap_for_symbol(exchange, s) for s in batch]
            await asyncio.gather(*tasks)
            
    finally:
        await exchange.close()
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
