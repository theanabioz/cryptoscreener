import ccxt.pro as ccxt  # Используем pro для async, но можно и обычный
import ccxt.async_support as ccxt_async
import pandas as pd
import asyncio
import os
import logging
from datetime import datetime, timedelta

# Настройки
TIMEFRAME = '1m'
DAYS = 90
DATA_DIR = '/data/raw_parquet' # Путь внутри Docker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def download_pair(exchange, symbol):
    filename = f"{DATA_DIR}/{symbol.replace('/', '')}.parquet"
    if os.path.exists(filename):
        logger.info(f"Skipping {symbol}, already exists.")
        return

    logger.info(f"Downloading {symbol}...")
    
    # Период: 90 дней назад -> Сейчас
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=DAYS)).timestamp() * 1000)
    
    all_candles = []
    current_time = start_time
    
    # Binance отдает максимум 1000 свечей
    while current_time < end_time:
        try:
            candles = await exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=1000, since=current_time)
            if not candles:
                break
            
            all_candles.extend(candles)
            current_time = candles[-1][0] + 60000 # +1 минута
            
            # Небольшой sleep, чтобы не дудосить
            await asyncio.sleep(0.05)
            
        except Exception as e:
            logger.error(f"Error {symbol}: {e}")
            await asyncio.sleep(5)
            continue

    if not all_candles:
        return

    # Сохраняем
    df = pd.DataFrame(all_candles, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    
    # Используем PyArrow для быстрого Parquet
    df.to_parquet(filename, engine='pyarrow', compression='snappy')
    logger.info(f"✅ Saved {symbol}: {len(df)} rows")

async def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    exchange = ccxt_async.binance({'enableRateLimit': True})
    
    try:
        # 1. Получаем список всех тикеров
        logger.info("Fetching all USDT pairs from Binance...")
        markets = await exchange.load_markets()
        
        # 2. Фильтруем USDT Spot
        symbols = [
            s for s in markets.keys() 
            if s.endswith('/USDT') and ':USDT' not in s
        ]
        
        logger.info(f"Found {len(symbols)} USDT pairs. Starting massive download...")
        
        # 3. Качаем
        for i, symbol in enumerate(symbols):
            logger.info(f"[{i+1}/{len(symbols)}] Processing {symbol}")
            await download_pair(exchange, symbol)
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
