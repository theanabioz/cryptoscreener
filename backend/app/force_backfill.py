import asyncio
import ccxt.async_support as ccxt
import logging
from datetime import datetime, timedelta, timezone
from database import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def backfill_symbol(exchange, symbol, days=7):
    """Докачивает историю для конкретной монеты за указанный период."""
    try:
        since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
        end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        total_injected = 0
        while since < end_ts:
            candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1000)
            if not candles:
                break
            
            await save_to_db(symbol, candles)
            total_injected += len(candles)
            since = candles[-1][0] + 60000 
            
            if len(candles) < 1000:
                break
                
            await asyncio.sleep(0.1) # Минимальная пауза между чанками одного символа

        logger.info(f"  [+] {symbol}: {total_injected} candles")
        return total_injected

    except Exception as e:
        logger.error(f"  [!] Error {symbol}: {e}")
        return 0

async def save_to_db(symbol, candles):
    records = []
    for c in candles:
        dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
        records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
    
    query = """
        INSERT INTO candles (time, symbol, open, high, low, close, volume)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (time, symbol) DO UPDATE SET
            high = GREATEST(candles.high, EXCLUDED.high),
            low = LEAST(candles.low, EXCLUDED.low),
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """
    async with db.pool.acquire() as conn:
        await conn.executemany(query, records)

async def main():
    logger.info("🚀 Starting MASSIVE Force Backfill (7 days for ALL symbols)...")
    await db.connect()
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Берем список активных монет
        rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]
        
        if not symbols:
            logger.warning("No active symbols in coins_meta. Fetching from candles...")
            rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles")
            symbols = [r['symbol'] for r in rows]

        logger.info(f"Targeting {len(symbols)} symbols. This will take some time...")
        
        for i, symbol in enumerate(symbols):
            logger.info(f"({i+1}/{len(symbols)}) Processing {symbol}...")
            await backfill_symbol(exchange, symbol, days=7)
            # Пауза между монетами для соблюдения лимитов API
            await asyncio.sleep(0.2)
            
    finally:
        await exchange.close()
        await db.close()
        logger.info("✅ MASSIVE Backfill finished.")

if __name__ == "__main__":
    asyncio.run(main())