import asyncio
import pandas as pd
import json
import logging
from database import db
from ta_lib import calculate_rsi, calculate_ema, calculate_macd, calculate_bollinger
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def update_all_indicators():
    """
    Тяжелая задача: берет данные для всех монет и считает индикаторы.
    Оптимизировано: меньше запросов к БД.
    """
    logger.info("🔄 Starting TA Calculation Cycle...")
    
    # 1. Получаем список активных символов
    coins = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
    if not coins:
        logger.warning("No active coins found in coins_meta. Checking candles...")
        coins = await db.fetch_all("SELECT DISTINCT symbol FROM candles LIMIT 1000")
    
    symbols = [r['symbol'] for r in coins]
    
    # 2. Обрабатываем пачками по 50 монет для стабильности
    batch_size = 50
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} symbols)")
        
        # Получаем историю свечей для всей пачки разом
        # Нам нужно ~200 свечей для каждой монеты
        symbols_placeholder = ", ".join([f"'{s}'" for s in batch])
        query = f"""
            SELECT 
                symbol,
                time_bucket('1h', time) AS time,
                LAST(close, time) as close,
                SUM(volume) as volume
            FROM candles
            WHERE symbol IN ({symbols_placeholder})
              AND time > NOW() - INTERVAL '10 days'
            GROUP BY symbol, time
            ORDER BY symbol, time ASC
        """
        
        try:
            rows = await db.fetch_all(query)
            if not rows:
                continue
                
            df_all = pd.DataFrame(rows, columns=['symbol', 'time', 'close', 'volume'])
            
            updates = []
            for symbol in batch:
                df = df_all[df_all['symbol'] == symbol].copy()
                if len(df) < 10:
                    continue
                
                close = df['close']
                
                # Расчет
                rsi = calculate_rsi(close, 14).iloc[-1]
                ema50 = calculate_ema(close, 50).iloc[-1]
                macd, macd_sig, macd_hist = calculate_macd(close)
                bb_up, bb_low = calculate_bollinger(close)
                
                # Спарклайн (24 точки)
                spark_data = close.tail(24).tolist()
                spark_json = json.dumps({"price": spark_data})
                
                updates.append((
                    float(close.iloc[-1]), # current_price (snapshot)
                    float(df['volume'].tail(24).sum()), # approx volume 24h
                    float(rsi) if not pd.isna(rsi) else None,
                    float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                    float(macd_sig.iloc[-1]) if not pd.isna(macd_sig.iloc[-1]) else None,
                    float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else None,
                    float(ema50) if not pd.isna(ema50) else None,
                    float(bb_up.iloc[-1]) if not pd.isna(bb_up.iloc[-1]) else None,
                    float(bb_low.iloc[-1]) if not pd.isna(bb_low.iloc[-1]) else None,
                    spark_json,
                    symbol
                ))

            if updates:
                query_update = """
                    UPDATE coin_status SET
                        updated_at = NOW(),
                        current_price = $1,
                        volume_24h = $2,
                        rsi_14 = $3,
                        macd = $4,
                        macd_signal = $5,
                        macd_hist = $6,
                        ema_50 = $7,
                        bb_upper = $8,
                        bb_lower = $9,
                        sparkline_in_7d = $10
                    WHERE symbol = $11
                """
                async with db.pool.acquire() as conn:
                    await conn.executemany(query_update, updates)
                    
        except Exception as e:
            logger.error(f"Error in batch: {e}")

    logger.info("✅ TA Cycle Finished.")

async def worker_loop():
    logger.info("🚀 TA Worker started")
    await db.connect()
    
    # Убедимся, что мета-данные есть
    from init_status_db import init_db
    await init_db()
    
    while True:
        try:
            await update_all_indicators()
        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
        
        # Раз в 5 минут достаточно для часовых индикаторов
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(worker_loop())