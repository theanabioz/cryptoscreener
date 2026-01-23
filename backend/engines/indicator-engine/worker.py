import asyncio
import sys
import os
import json
import pandas as pd
import pandas_ta as ta
import numpy as np

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def process_task(symbol):
    """Вычисляет массив индикаторов (The Beast Mode) для всех таймфреймов."""
    try:
        # Для качественного расчета 200 индикаторов нам нужно хотя бы 300 свечей
        # Запрашиваем 1м свечи и будем их ресемплить (это быстрее и точнее)
        query = """
            SELECT time, open, high, low, close, volume
            FROM candles
            WHERE symbol = $1 AND time > NOW() - INTERVAL '7 days'
            ORDER BY time ASC
        """
        rows = await db.fetch_all(query, symbol)
        if len(rows) < 100: return

        df = pd.DataFrame(rows, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('time', inplace=True)
        
        results = {}
        # Таймфреймы для расчета
        timeframes = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }

        for tf_code, tf_resample in timeframes.items():
            # 1. Ресемплинг данных под нужный таймфрейм
            df_tf = df.resample(tf_resample).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

            if len(df_tf) < 20: continue

            # 2. МАССОВЫЙ РАСЧЕТ ИНДИКАТОРОВ (pandas-ta)
            # Мы используем встроенную стратегию 'All', чтобы посчитать максимум возможного
            # Или настраиваем свой список 'The Beast'
            df_tf.ta.strategy("All") # Это посчитает ~150-200 индикаторов одним махом!

            # 3. Подготовка JSON
            # Берем последнюю строку (текущие значения)
            latest = df_tf.iloc[-1].replace({np.nan: None}).to_dict()
            
            # Убираем базовые OHLC, оставляем только индикаторы
            indicator_data = {k: v for k, v in latest.items() if k not in ['open', 'high', 'low', 'close', 'volume']}
            results[tf_code] = indicator_data

        # 4. Сохранение в БД
        query_update = f"""
            UPDATE coin_status SET
                updated_at = NOW(),
                current_price = $1,
                indicators_1m = $2,
                indicators_5m = $3,
                indicators_15m = $4,
                indicators_1h = $5,
                indicators_4h = $6,
                indicators_1d = $7
            WHERE symbol = $8
        """
        await db.execute(
            query_update,
            float(df['close'].iloc[-1]),
            json.dumps(results.get('1m')),
            json.dumps(results.get('5m')),
            json.dumps(results.get('15m')),
            json.dumps(results.get('1h')),
            json.dumps(results.get('4h')),
            json.dumps(results.get('1d')),
            symbol
        )
        print(f"  [BEAST] {symbol}: All indicators calculated.", flush=True)

    except Exception as e:
        print(f"  [!] BEAST Error {symbol}: {e}", flush=True)

async def run_worker():
    print("🚀 Indicator Engine v3 (THE BEAST) started", flush=True)
    await db.connect()
    
    try:
        await db.redis.xgroup_create("ta_tasks", "beast_group", id="0", mkstream=True)
    except Exception: pass

    while True:
        try:
            response = await db.redis.xreadgroup("beast_group", "worker_beast", {"ta_tasks": ">"}, count=1, block=5000)
            if response:
                stream_name, messages = response[0]
                msg_id, data = messages[0]
                symbol = data['symbol']
                
                await process_task(symbol)
                await db.redis.xack("ta_tasks", "beast_group", msg_id)
        except Exception as e:
            print(f"❌ Beast Worker Error: {e}", flush=True)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())