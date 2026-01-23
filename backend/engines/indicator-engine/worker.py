import asyncio
import sys
import os
import json
import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings

# Глушим шум
warnings.filterwarnings("ignore")

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def process_task(symbol):
    """Векторизированный расчет ТОП-25 индикаторов."""
    try:
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
        timeframes = {'1m': '1min', '5m': '5min', '15m': '15min', '1h': '1h', '4h': '4h', '1d': '1D'}

        for tf_code, tf_resample in timeframes.items():
            df_tf = df.resample(tf_resample).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 
                'close': 'last', 'volume': 'sum'
            }).dropna()

            if len(df_tf) < 52: continue

            # ВЕКТОРНЫЙ РАСЧЕТ (Самый быстрый способ в pandas-ta)
            df_tf.ta.cores = 1
            df_tf.ta.rsi(length=14, append=True)
            df_tf.ta.macd(append=True)
            df_tf.ta.ema(length=50, append=True)
            df_tf.ta.ema(length=200, append=True)
            df_tf.ta.bbands(append=True)
            df_tf.ta.supertrend(append=True)
            # Добавьте другие если нужно...

            # Упаковка
            latest = df_tf.iloc[-1].replace({np.nan: None}).to_dict()
            indicator_data = {k: (round(float(v), 6) if isinstance(v, (int, float)) else v) 
                             for k, v in latest.items() 
                             if k not in ['open', 'high', 'low', 'close', 'volume']}
            results[tf_code] = indicator_data

        # UPDATE JSONB
        query_update = """
            UPDATE coin_status SET updated_at = NOW(), current_price = $1,
                indicators_1m = $2, indicators_5m = $3, indicators_15m = $4,
                indicators_1h = $5, indicators_4h = $6, indicators_1d = $7
            WHERE symbol = $8
        """
        await db.execute(query_update, float(df['close'].iloc[-1]),
            json.dumps(results.get('1m')), json.dumps(results.get('5m')), json.dumps(results.get('15m')),
            json.dumps(results.get('1h')), json.dumps(results.get('4h')), json.dumps(results.get('1d')),
            symbol
        )
        return True
    except Exception as e:
        print(f"  [!] Error {symbol}: {e}", flush=True)
        return False

async def run_worker():
    worker_id = os.environ.get('HOSTNAME', 'worker-1')
    print(f"🚀 {worker_id} started (Vectorized Mode)", flush=True)
    await db.connect()
    
    stream_key = "ta_tasks"
    group_name = "beast_group"

    while True:
        try:
            # Читаем новые задачи
            response = await db.redis.xreadgroup(group_name, worker_id, {stream_key: ">"}, count=1, block=2000)
            if response:
                msg_id, data = response[0][1][0]
                symbol = data['symbol']
                # print(f"  [{worker_id}] Processing {symbol}")
                success = await process_task(symbol)
                await db.redis.xack(stream_key, group_name, msg_id)
        except Exception as e:
            if "NOGROUP" in str(e):
                try: await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
                except: pass
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())
