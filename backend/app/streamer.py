import asyncio
import ccxt.pro as ccxt
import logging
import os
from datetime import datetime, timezone
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_streamer():
    logger.info("🚀 Starting WebSocket Streamer...")
    
    # 1. Подключаемся к БД
    await db.connect()
    
    # 2. Инициализируем биржу
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # 3. Загружаем список рынков (чтобы знать, на что подписываться)
        # Получаем список монет из нашей базы (только активные)
        symbols_rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles")
        target_symbols = [r['symbol'] for r in symbols_rows]
        
        if not target_symbols:
            logger.warning("No symbols found in DB. Fallback to top pairs.")
            target_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

        logger.info(f"📡 Subscribing to {len(target_symbols)} pairs...")

        # 4. Основной цикл
        while True:
            try:
                # watch_ohlcv может принимать список символов
                # Но CCXT для Binance требует мультиплексирования. 
                # Лучше использовать watch_tickers для лайв цены или watch_ohlcv для свечей.
                # Для 450 пар watch_ohlcv может быть тяжелым. Попробуем пачками.
                
                # ВАЖНО: Binance WS лимит - 1024 подписки на соединение. У нас 450, влезаем.
                
                # Получаем обновления
                # watch_ohlcv возвращает список [timestamp, open, high, low, close, volume]
                # но он ждет обновления для КОНКРЕТНОГО символа.
                # Чтобы слушать ВСЕ, нужно использовать loop.
                
                # Альтернатива: watch_tickers (легче) -> но нам нужны OHLCV для истории.
                # Идем по пути watch_ohlcv_for_symbols
                
                # Разбиваем на пачки, если нужно, но пока попробуем все сразу
                # CCXT pro сам разрулит мультиплексирование
                
                candles = await exchange.watch_ohlcv_for_symbols(target_symbols, '1m')
                
                # candles - это словарь { symbol: [[t,o,h,l,c,v], ...] }
                # или список изменений. Зависит от реализации watch_ohlcv_for_symbols (она возвращает changes)
                
                # Обработка полученных данных
                # В CCXT watch_ohlcv_for_symbols возвращает данные для тех пар, которые обновились
                # Но структура возврата сложная. Проще использовать watch_ohlcv в цикле для каждого? Нет, это заблокирует.
                
                # Правильный паттерн для CCXT Pro (Multi-symbol):
                # Просто вызываем await и он вернет то, что пришло первым.
                
                # ПРИМЕЧАНИЕ: watch_ohlcv_for_symbols в python версии возвращает словарь обновленных свечей
                
                if not candles:
                    continue
                    
                # Готовим пачку для записи
                records = []
                for symbol, ohlcvs in candles.items():
                    # Берем последнюю свечу (она самая свежая)
                    c = ohlcvs[-1]
                    timestamp = c[0]
                    dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                    
                    # (time, symbol, open, high, low, close, volume)
                    records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
                
                if records:
                    # UPSERT (Вставка или обновление)
                    # Это позволяет видеть "живую" свечу до её закрытия
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
                        
                    # Логируем редко, чтобы не спамить
                    # logger.info(f"Updated {len(records)} candles")

            except Exception as e:
                logger.error(f"Stream error: {e}")
                await asyncio.sleep(5) # Пауза перед реконнектом

    finally:
        await exchange.close()
        await db.close()

if __name__ == "__main__":
    asyncio.run(run_streamer())
