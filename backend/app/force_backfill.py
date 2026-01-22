import asyncio
import ccxt.async_support as ccxt
import logging
from datetime import datetime, timedelta, timezone
from database import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def backfill(symbol, days=7):
    logger.info(f"🚀 Starting FORCE backfill for {symbol} ({days} days)...")
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Binance отдает макс 1000 свечей за раз. 
        # В 7 днях = 7 * 24 * 60 = 10080 минут.
        # Нам нужно сделать ~11 запросов.
        
        since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
        all_candles = []
        
        while since < int(datetime.now(timezone.utc).timestamp() * 1000):
            logger.info(f"Fetching {symbol} starting from {datetime.fromtimestamp(since/1000, tz=timezone.utc)}")
            candles = await exchange.fetch_ohlcv(symbol, '1m', since=since, limit=1000)
            if not candles:
                break
            
            all_candles.extend(candles)
            since = candles[-1][0] + 60000 # Следующая минута
            
            # Сохраняем пачкой
            await save_to_db(symbol, candles)
            
            if len(candles) < 1000: # Дошли до текущего момента
                break
                
            await asyncio.sleep(0.5) # Rate limit protection

        logger.info(f"✅ Finished {symbol}. Total candles injected: {len(all_candles)}")

    except Exception as e:
        logger.error(f"Error backfilling {symbol}: {e}")
    finally:
        await exchange.close()

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
    await db.connect()
    # Фокусируемся на главных монетах, где дыры
    await backfill('BTC/USDT', days=7)
    await backfill('ETH/USDT', days=7)
    await backfill('SOL/USDT', days=7)
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
