import asyncio
import pandas as pd
import json
from database import db
from ta_lib import calculate_rsi, calculate_ema, calculate_macd, calculate_bollinger
import time

async def process_batch(symbols):
    """
    Берет пачку символов, качает для них историю, считает индикаторы и сохраняет.
    """
    if not symbols:
        return

    # 1. Получаем свечи (последние 200 штук для точности индикаторов)
    # Используем time_bucket('1h') для часовых индикаторов (или 15m, как решим)
    # Для скринера обычно смотрят 1H или 4H. Давайте начнем с 1H.
    
    total = len(symbols)
    for i, symbol in enumerate(symbols):
        try:
            if (i + 1) % 10 == 0 or i == 0:
                print(f"[{i+1}/{total}] Processing {symbol}...")
            
            # Получаем 200 последних часовых свечей
            # (Код похож на klines.py, но внутри python)
            query = """
                SELECT 
                    time_bucket('1h', time) AS time,
                    LAST(close, time) as close,
                    SUM(volume) as volume
                FROM candles
                WHERE symbol = $1
                GROUP BY time
                ORDER BY time DESC
                LIMIT 200
            """
            rows = await db.fetch_all(query, symbol)
            
            if not rows or len(rows) < 24: # Минимум 24 для спарклайна
                continue

            # Превращаем в DataFrame и сортируем по времени (ASC)
            df = pd.DataFrame(rows, columns=['time', 'close', 'volume'])
            df = df.sort_values('time').reset_index(drop=True)
            
            # --- РАСЧЕТ ИНДИКАТОРОВ ---
            close = df['close']
            
            # RSI 14
            df['rsi'] = calculate_rsi(close, 14)
            
            # EMA 50
            df['ema_50'] = calculate_ema(close, 50)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(close)
            
            # Bollinger Bands
            df['bb_upper'], df['bb_lower'] = calculate_bollinger(close)
            
            # Берем ПОСЛЕДНЕЕ значение (текущее состояние)
            last = df.iloc[-1]
            
            # Спарклайн (последние 24 точки или меньше)
            sparkline_data = close.tail(24).tolist()
            sparkline_json = json.dumps(sparkline_data)
            
            # --- СОХРАНЕНИЕ В DB ---
            # Upsert (Вставить или Обновить)
            update_query = """
                INSERT INTO coin_status (
                    symbol, updated_at, 
                    current_price, volume_24h, 
                    rsi_14, macd, macd_signal, macd_hist, ema_50, bb_upper, bb_lower,
                    sparkline
                ) VALUES ($1, NOW(), $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (symbol) DO UPDATE SET
                    updated_at = NOW(),
                    current_price = EXCLUDED.current_price,
                    volume_24h = EXCLUDED.volume_24h,
                    rsi_14 = EXCLUDED.rsi_14,
                    macd = EXCLUDED.macd,
                    macd_signal = EXCLUDED.macd_signal,
                    macd_hist = EXCLUDED.macd_hist,
                    ema_50 = EXCLUDED.ema_50,
                    bb_upper = EXCLUDED.bb_upper,
                    bb_lower = EXCLUDED.bb_lower,
                    sparkline = EXCLUDED.sparkline;
            """
            
            await db.pool.execute(
                update_query,
                symbol,
                float(last['close']),
                float(last['volume']), 
                float(last['rsi']) if not pd.isna(last['rsi']) else None,
                float(last['macd']) if not pd.isna(last['macd']) else None,
                float(last['macd_signal']) if not pd.isna(last['macd_signal']) else None,
                float(last['macd_hist']) if not pd.isna(last['macd_hist']) else None,
                float(last['ema_50']) if not pd.isna(last['ema_50']) else None,
                float(last['bb_upper']) if not pd.isna(last['bb_upper']) else None,
                float(last['bb_lower']) if not pd.isna(last['bb_lower']) else None,
                sparkline_json
            )
            # print(f"Updated {symbol}: RSI={last['rsi']:.2f}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

async def worker_loop():
    print("🚀 TA Worker started", flush=True)
    try:
        await db.connect()
        print("✅ DB Connected", flush=True)
    except Exception as e:
        print(f"❌ DB Connection failed: {e}", flush=True)
        return
    
    # Сначала создаем таблицу если нет
    from init_status_db import init_db
    await init_db()
    
    while True:
        start_time = time.time()
        print("🔍 Fetching symbols...", flush=True)
        
        # 1. Получаем список всех монет из мета-таблицы (Мгновенно)
        coins = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        
        if not coins:
             print("⚠️ No coins in coins_meta. Filling from candles...", flush=True)
             # Fallback если база "старая"
             coins = await db.fetch_all("SELECT DISTINCT symbol FROM candles WHERE time > NOW() - INTERVAL '24 hours'")
             if not coins:
                 coins = await db.fetch_all("SELECT DISTINCT symbol FROM candles LIMIT 1000")
             
        symbols = list(set([r['symbol'] for r in coins])) # Убираем дубли на всякий случай
        
        print(f"📊 Analyzing {len(symbols)} coins...", flush=True)
        
        await process_batch(symbols)
        
        elapsed = time.time() - start_time
        print(f"✅ Cycle finished in {elapsed:.2f}s. Sleeping...", flush=True)
        
        # Спим 1 минуту перед следующим обновлением
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(worker_loop())
