import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import os
import logging
from datetime import datetime, timedelta

# Настройки
TIMEFRAME = '1m'
YEARS = 2
DATA_DIR = 'data/history'
BATCH_SIZE = 1000 # Лимит свечей за один запрос у Binance

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def download_pair(exchange, symbol):
    """Скачивает историю для одной пары"""
    filename = f"{DATA_DIR}/{symbol.replace('/', '')}_{TIMEFRAME}.parquet"
    
    # Если файл уже есть, пропускаем (или можно докачивать, но пока просто пропуск)
    if os.path.exists(filename):
        logger.info(f"Skipping {symbol}, already exists.")
        return

    logger.info(f"Starting download for {symbol}...")
    
    # Вычисляем время старта (2 года назад)
    start_date = datetime.now() - timedelta(days=YEARS * 365)
    since = int(start_date.timestamp() * 1000)
    now = int(datetime.now().timestamp() * 1000)
    
    all_candles = []
    
    while since < now:
        try:
            candles = await exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=BATCH_SIZE, since=since)
            
            if not candles:
                break
            
            all_candles.extend(candles)
            
            # Обновляем курсор времени (время последней свечи + 1 минута)
            last_timestamp = candles[-1][0]
            since = last_timestamp + 60000 
            
            # Небольшая пауза, чтобы не забанили, хотя enableRateLimit справляется
            # await asyncio.sleep(0.1) 
            
            # Лог прогресса для длинных скачиваний
            if len(all_candles) % 50000 == 0:
                logger.info(f"  {symbol}: Loaded {len(all_candles)} candles...")
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            await asyncio.sleep(5) # Ждем и пробуем снова (или пропускаем итерацию)
            continue

    if not all_candles:
        logger.warning(f"No data for {symbol}")
        return

    # Сохраняем в Parquet
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Создаем папку если нет
    os.makedirs(DATA_DIR, exist_ok=True)
    
    df.to_parquet(filename, index=False)
    logger.info(f"✅ Saved {symbol}: {len(df)} rows to {filename}")

async def main():
    # Создаем папку для данных
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Инициализируем биржу с Rate Limit (чтобы сама ждала)
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    try:
        # Получаем список всех пар USDT
        markets = await exchange.load_markets()
        symbols = [
            s for s in markets.keys() 
            if s.endswith('/USDT') and ':USDT' not in s # Исключаем фьючерсы с ":"
        ]
        
        logger.info(f"Found {len(symbols)} USDT pairs. Starting download...")
        
        # Скачиваем последовательно (или небольшими пачками), чтобы не умереть по RAM
        # Для надежности лучше по одному, так как процесс долгий
        for i, symbol in enumerate(symbols):
            logger.info(f"[{i+1}/{len(symbols)}] Processing {symbol}")
            await download_pair(exchange, symbol)
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Download stopped by user")
