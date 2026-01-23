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
    """Вычисляет ТОП-25 самых мощных индикаторов (Optimized Beast)."""
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
        timeframes = {
            '1m': '1min', '5m': '5min', '15m': '15min', 
            '1h': '1h', '4h': '4h', '1d': '1D'
        }

        # Создаем кастомную стратегию "The Professional"
        # Мы выбираем только то, что реально работает и не дублирует друг друга
        pro_strategy = ta.Strategy(
            name="The Professional",
            description="25 Essential Indicators for Strategy Building",
            ta=[
                {"kind": "rsi", "length": 14},
                {"kind": "stochrsi", "length": 14},
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
                {"kind": "ema", "length": 20},
                {"kind": "ema", "length": 50},
                {"kind": "ema", "length": 100},
                {"kind": "ema", "length": 200},
                {"kind": "bbands", "length": 20, "std": 2},
                {"kind": "atr", "length": 14},
                {"kind": "adx", "length": 14},
                {"kind": "mfi", "length": 14},
                {"kind": "obv"},
                {"kind": "supertrend", "period": 10, "multiplier": 3},
                {"kind": "cmf", "length": 20},
                # Ichimoku Cloud (основные компоненты)
                {"kind": "ichimoku", "tenkan": 9, "kijun": 26, "senkou": 52}
            ]
        )

        for tf_code, tf_resample in timeframes.items():
            df_tf = df.resample(tf_resample).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 
                'close': 'last', 'volume': 'sum'
            }).dropna()

            if len(df_tf) < 52: continue # Минимум для Ишимоку

            # Расчет нашей PRO стратегии
            df_tf.ta.cores = 0 # Отключаем внутреннюю многопоточность для стабильности в Docker
            df_tf.ta.study(pro_strategy)

            # Подготовка данных
            latest = df_tf.iloc[-1].replace({np.nan: None}).to_dict()
            indicator_data = {}
            for k, v in latest.items():
                if k in ['open', 'high', 'low', 'close', 'volume']: continue
                if isinstance(v, (int, float)):
                    indicator_data[k] = round(float(v), 6)
                else:
                    indicator_data[k] = v
            
            results[tf_code] = indicator_data

        # Сохранение в базу
        query_update = """
            UPDATE coin_status SET
                updated_at = NOW(),
                current_price = $1,
                indicators_1m = $2, indicators_5m = $3, indicators_15m = $4,
                indicators_1h = $5, indicators_4h = $6, indicators_1d = $7
            WHERE symbol = $8
        """
        await db.execute(
            query_update,
            float(df['close'].iloc[-1]),
            json.dumps(results.get('1m')), json.dumps(results.get('5m')), json.dumps(results.get('15m')),
            json.dumps(results.get('1h')), json.dumps(results.get('4h')), json.dumps(results.get('1d')),
            symbol
        )
        print(f"  [PRO-V3.2] {symbol}: Optimized indicators updated.", flush=True)

    except Exception as e:
        print(f"  [!] Error processing {symbol}: {e}", flush=True)

async def run_worker():
    print("🚀 Indicator Engine v3.2 (PRO OPTIMIZED) is ready", flush=True)
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
                await process_task(symbol)
                await db.redis.xack("ta_tasks", "beast_group", msg_id)
        except Exception as e:
            print(f"❌ Worker Error: {e}", flush=True)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())