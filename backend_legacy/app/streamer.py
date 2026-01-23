import asyncio
import ccxt.pro as ccxt
import logging
import os
import json
from datetime import datetime, timezone
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_streamer():
    logger.info("🚀 Starting Binance Unified Streamer (!miniTicker@arr)...")
    
    await db.connect()
    
    # Мы используем сырой aiohttp для miniTicker, так как это быстрее и проще для общего потока
    # Но можно и через CCXT, если использовать watch_tickers
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    queue = asyncio.Queue()

    async def db_writer():
        batch_size = 500
        buffer = []
        while True:
            item = await queue.get()
            buffer.append(item)
            
            # Собираем пачку
            try:
                while len(buffer) < batch_size:
                    buffer.append(queue.get_nowait())
            except asyncio.QueueEmpty:
                pass
            
            if buffer:
                records = []
                for symbol, c in buffer:
                    # c = [timestamp, open, high, low, close, volume]
                    dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                    records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
                
                try:
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
                except Exception as e:
                    logger.error(f"DB Write Error: {e}")
                
                buffer.clear()
            await asyncio.sleep(1)

    asyncio.create_task(db_writer())

    while True:
        try:
            # watch_tickers без аргументов в Binance Pro слушает поток !ticker@arr или !miniTicker@arr
            # Это дает данные ПО ВСЕМ парам сразу в одном соединении.
            tickers = await exchange.watch_tickers()
            
            if tickers:
                for symbol, ticker in tickers.items():
                    if not symbol.endswith('/USDT'):
                        continue
                        
                    # Формируем данные для Redis и БД
                    # ticker в CCXT содержит 'last', 'open', 'high', 'low', 'baseVolume', 'timestamp'
                    timestamp = ticker['timestamp'] or int(datetime.now().timestamp() * 1000)
                    
                    candle = [
                        timestamp,
                        ticker['open'],
                        ticker['high'],
                        ticker['low'],
                        ticker['last'],
                        ticker['baseVolume']
                    ]

                    # 1. Публикуем в Redis для фронтенда
                    if db.redis:
                        payload = {"s": symbol, "k": candle}
                        await db.redis.publish("crypto_updates", json.dumps(payload))

                    # 2. В очередь для БД
                    await queue.put((symbol, candle))
                    
        except Exception as e:
            logger.error(f"Streamer Error: {e}")
            await asyncio.sleep(5)
            # Пересоздаем exchange при ошибке
            await exchange.close()
            exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

if __name__ == "__main__":
    asyncio.run(run_streamer())
