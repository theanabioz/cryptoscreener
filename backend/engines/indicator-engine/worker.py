import asyncio
import sys
import os
import json
import pandas as pd

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db
from common.ta_lib import calculate_rsi, calculate_ema, calculate_macd, calculate_bollinger

async def process_task(symbol):
    """Выполняет расчет ТА для одной монеты."""
    try:
        # 1. Берем историю из БД (10 дней достаточно для часовых индикаторов)
        query = """
            SELECT 
                time_bucket('1h', time) AS time,
                LAST(close, time) as close,
                SUM(volume) as volume
            FROM candles
            WHERE symbol = $1 AND time > NOW() - INTERVAL '10 days'
            GROUP BY time
            ORDER BY time ASC
        """
        rows = await db.fetch_all(query, symbol)
        if len(rows) < 20: return # Мало данных

        df = pd.DataFrame(rows, columns=['time', 'close', 'volume'])
        close = df['close']
        
        # 2. Расчет
        rsi = calculate_rsi(close, 14).iloc[-1]
        ema50 = calculate_ema(close, 50).iloc[-1]
        macd, macd_sig, macd_hist = calculate_macd(close)
        bb_up, bb_low = calculate_bollinger(close)
        
        spark_data = close.tail(24).tolist()
        spark_json = json.dumps({"price": spark_data})

        # 3. Сохранение результата
        query_update = """
            UPDATE coin_status SET
                updated_at = NOW(),
                current_price = $1,
                rsi_14 = $2,
                macd = $3,
                macd_signal = $4,
                ema_50 = $5,
                bb_upper = $6,
                bb_lower = $7,
                sparkline_in_7d = $8
            WHERE symbol = $9
        """
        await db.execute(
            query_update,
            float(close.iloc[-1]),
            float(rsi) if not pd.isna(rsi) else None,
            float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
            float(macd_sig.iloc[-1]) if not pd.isna(macd_sig.iloc[-1]) else None,
            float(ema50) if not pd.isna(ema50) else None,
            float(bb_up.iloc[-1]) if not pd.isna(bb_up.iloc[-1]) else None,
            float(bb_low.iloc[-1]) if not pd.isna(bb_low.iloc[-1]) else None,
            spark_json,
            symbol
        )
    except Exception as e:
        print(f"  [!] Error processing {symbol}: {e}", flush=True)

async def run_worker():
    print("👷 Indicator Engine: Worker started", flush=True)
    await db.connect()
    
    # Создаем группу потребителей для Redis Streams (если нет)
    # Это позволяет запустить 10 воркеров, и каждый будет получать СВОИ задачи
    try:
        await db.redis.xgroup_create("ta_tasks", "worker_group", id="0", mkstream=True)
    except Exception: pass # Группа уже существует

    while True:
        try:
            # Читаем одну задачу из стрима
            # block=5000 (ждать задачу 5 сек)
            response = await db.redis.xreadgroup("worker_group", "worker_1", {"ta_tasks": ">"}, count=1, block=5000)
            
            if response:
                # response: [['ta_tasks', [('id', {'symbol': 'BTC/USDT'})]]]
                stream_name, messages = response[0]
                msg_id, data = messages[0]
                symbol = data['symbol']
                
                await process_task(symbol)
                
                # Подтверждаем выполнение (ACK)
                await db.redis.xack("ta_tasks", "worker_group", msg_id)
            
        except Exception as e:
            print(f"❌ Worker Error: {e}", flush=True)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())
