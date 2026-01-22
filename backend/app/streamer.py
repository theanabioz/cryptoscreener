import asyncio
import ccxt.pro as ccxt
import logging
import os
from datetime import datetime, timezone
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def stream_symbol(exchange, symbol, queue):
    """
    Постоянно слушает OHLCV для одного символа и кладет обновления в очередь.
    """
    retries = 0
    while True:
        try:
            # watch_ohlcv возвращает список свечей. Ждет прихода обновления.
            candles = await exchange.watch_ohlcv(symbol, '1m')
            
            if candles:
                # Берем последнюю свечу (она самая свежая)
                latest_candle = candles[-1]
                # Кладем в очередь: (symbol, candle_data)
                await queue.put((symbol, latest_candle))
                
            retries = 0 # Сброс счетчика ошибок при успехе
            
        except Exception as e:
            retries += 1
            # Пауза с экспоненциальным отступом, но не более 60 сек
            wait_time = min(5 * retries, 60)
            logger.warning(f"Error watching {symbol}: {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

async def db_writer(queue):
    """
    Читает из очереди и делает пакетную вставку в БД.
    """
    logger.info("💾 DB Writer started")
    batch_size = 30 # Оптимальный размер пачки для баланса между realtime и нагрузкой
    buffer = []
    
    while True:
        try:
            # 1. Собираем сообщения
            # Ждем хотя бы одно
            item = await queue.get()
            buffer.append(item)
            
            # Пытаемся добрать еще из очереди без ожидания
            try:
                while len(buffer) < batch_size:
                    buffer.append(queue.get_nowait())
            except asyncio.QueueEmpty:
                pass
            
            # Если буфер не полный, даем небольшой шанс накопиться еще данным
            if len(buffer) < batch_size:
                await asyncio.sleep(0.2)
                try:
                    while len(buffer) < batch_size:
                        buffer.append(queue.get_nowait())
                except asyncio.QueueEmpty:
                    pass

            # 2. Подготовка данных
            records = []
            for symbol, c in buffer:
                # c = [timestamp, open, high, low, close, volume]
                timestamp = c[0]
                dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
            
            # 3. Запись в БД
            if records:
                # UPSERT (Вставка или обновление)
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
                
                # logger.info(f"Updated {len(records)} candles")

            buffer.clear()
            
        except Exception as e:
            logger.error(f"DB Writer error: {e}")
            await asyncio.sleep(1)

async def run_streamer():
    logger.info("🚀 Starting WebSocket Streamer (Multi-Stream Mode)...")
    
    await db.connect()
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Загружаем список символов
        symbols_rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles")
        target_symbols = [r['symbol'] for r in symbols_rows]
        
        if not target_symbols:
            logger.warning("No symbols found in DB. Fallback to top pairs.")
            target_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

        logger.info(f"📡 Subscribing to {len(target_symbols)} pairs...")
        
        queue = asyncio.Queue()
        
        # Создаем задачи
        tasks = []
        
        # Запускаем писателя
        tasks.append(asyncio.create_task(db_writer(queue)))
        
        # Запускаем слушателей для каждого символа
        for symbol in target_symbols:
            tasks.append(asyncio.create_task(stream_symbol(exchange, symbol, queue)))
            
        # Ждем выполнения всех задач (они бесконечные)
        await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        await exchange.close()
        await db.close()

if __name__ == "__main__":
    asyncio.run(run_streamer())