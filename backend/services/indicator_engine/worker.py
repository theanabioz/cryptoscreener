import asyncio
import json
import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from common.database import db

warnings.simplefilter(action='ignore', category=FutureWarning)

async def worker_task(worker_id, symbols):
    print(f"🔧 Worker {worker_id}: Init ({len(symbols)} coins)", flush=True)
    
    await db.connect()
    cache = {}
    
    # WARMUP
    if symbols:
        print(f"🔥 Worker {worker_id}: Loading history...", flush=True)
        sym_str = ",".join([f"'{s}'" for s in symbols])
        query = f"""
            SELECT symbol, time, open, high, low, close, volume
            FROM candles
            WHERE symbol IN ({sym_str}) 
              AND time > NOW() - INTERVAL '3 days'
            ORDER BY time ASC
        """
        rows = await db.fetch_all(query)
        
        df_master = pd.DataFrame(rows, columns=['symbol', 'time', 'open', 'high', 'low', 'close', 'volume'])
        if not df_master.empty:
            df_master['time'] = pd.to_datetime(df_master['time'])
            df_master.set_index('time', inplace=True)
            for s in symbols:
                df = df_master[df_master['symbol'] == s]
                if not df.empty:
                    # Keep necessary columns
                    cache[s] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    
    print(f"✅ Worker {worker_id}: Ready.", flush=True)
    
    pubsub = db.redis.pubsub()
    await pubsub.subscribe("crypto_ticks")
    
    # Buffer for DB writes
    updates = {}
    last_write = time.time()

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                symbol = data['s']
                if symbol not in symbols: continue
                
                price = float(data['p'])
                ts = pd.to_datetime(data['t'], unit='ms').floor('1min')
                
                # Update Cache
                if symbol not in cache:
                    cache[symbol] = pd.DataFrame(
                        {'open': [price], 'high': [price], 'low': [price], 'close': [price], 'volume': [0.0]}, 
                        index=[ts]
                    )
                else:
                    df = cache[symbol]
                    if ts in df.index:
                        df.at[ts, 'close'] = price
                        df.at[ts, 'high'] = max(df.at[ts, 'high'], price)
                        df.at[ts, 'low'] = min(df.at[ts, 'low'], price)
                    else:
                        new_row = pd.DataFrame(
                            {'open': [price], 'high': [price], 'low': [price], 'close': [price], 'volume': [0.0]}, 
                            index=[ts]
                        )
                        df = pd.concat([df, new_row])
                        if len(df) > 500: df = df.iloc[-500:]
                        cache[symbol] = df
                
                # CALCULATION (1m)
                df = cache[symbol]
                if len(df) < 20: continue
                
                # Example: RSI 14
                rsi = ta.rsi(df['close'], length=14)
                rsi_val = rsi.iloc[-1] if rsi is not None and not pd.isna(rsi.iloc[-1]) else None
                
                # Buffer update
                updates[symbol] = (price, json.dumps({'rsi': rsi_val}))
                
                # Flush every 0.5s or 100 items
                if len(updates) > 100 or (time.time() - last_write > 0.5):
                    # Convert to list for executemany
                    batch = [(p, i, s) for s, (p, i) in updates.items()]
                    q = "UPDATE coin_status SET current_price=$1, indicators_1m=$2, updated_at=NOW() WHERE symbol=$3"
                    
                    async with db.pool.acquire() as conn:
                        await conn.executemany(q, batch)
                    
                    updates.clear()
                    last_write = time.time()
                    
            except Exception as e:
                pass

def start_worker(worker_id, symbols):
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        asyncio.run(worker_task(worker_id, symbols))
    except KeyboardInterrupt:
        pass
