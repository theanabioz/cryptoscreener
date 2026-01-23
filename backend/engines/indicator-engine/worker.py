import asyncio
import sys
import os
import json
import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings

# Глушим предупреждения библиотек (Pandas4Warning, DeprecationWarning и т.д.)
warnings.filterwarnings("ignore")

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def process_task(symbol):
    """Вычисляет ТОП-25 индикаторов через прямые вызовы pandas-ta."""
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

            # ПРЯМЫЕ ВЫЗОВЫ (Работает во всех версиях)
            df_tf.ta.rsi(length=14, append=True)
            df_tf.ta.macd(fast=12, slow=26, signal=9, append=True)
            df_tf.ta.ema(length=20, append=True)
            df_tf.ta.ema(length=50, append=True)
            df_tf.ta.ema(length=100, append=True)
            df_tf.ta.ema(length=200, append=True)
            df_tf.ta.bbands(length=20, std=2, append=True)
            df_tf.ta.atr(length=14, append=True)
            df_tf.ta.adx(length=14, append=True)
            df_tf.ta.mfi(length=14, append=True)
            df_tf.ta.supertrend(period=10, multiplier=3, append=True)
            df_tf.ta.ichimoku(append=True)

            # Очистка и упаковка
            latest = df_tf.iloc[-1].replace({np.nan: None}).to_dict()
            indicator_data = {k: (round(float(v), 6) if isinstance(v, (int, float)) else v) 
                             for k, v in latest.items() 
                             if k not in ['open', 'high', 'low', 'close', 'volume']}
            
            results[tf_code] = indicator_data

        # Сохранение
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
        print(f"  [BEAST] {symbol}: Success.", flush=True)

    except Exception as e:
        print(f"  [!] Error {symbol}: {e}", flush=True)

async def run_worker():
    print("🚀 Indicator Engine v3.3 (SOLID) started", flush=True)
    await db.connect()
    try:
        await db.redis.xgroup_create("ta_tasks", "beast_group", id="0", mkstream=True)
    except: pass
    while True:
        try:
            response = await db.redis.xreadgroup("beast_group", "worker_beast", {"ta_tasks": ">"}, count=1, block=5000)
            if response:
                stream_name, messages = response[0]
                msg_id, data = messages[0]
                symbol = data['symbol']
                print(f"🛠️ [WORKING] {symbol}: Starting indicators calc...", flush=True)
                await process_task(symbol)
                await db.redis.xack("ta_tasks", "beast_group", msg_id)
        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())
