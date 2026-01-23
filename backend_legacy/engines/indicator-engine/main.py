import asyncio
import multiprocessing
import os
import sys
import json
import uvloop
from redis import asyncio as aioredis
from stateful_worker import StatefulIndicatorWorker
# PYTHONPATH set to /app in Docker, so 'common' is accessible directly
from common.database import DatabasePool, db as main_db

async def worker_process(shard_id, symbols, redis_url, db_dsn):
    """
    Точка входа для дочернего процесса.
    """
    # 1. Setup Event Loop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    # 2. Init DB & Redis (Each process needs its own connection)
    local_db = DatabasePool() 
    # Manual connect
    await local_db.connect() 
    
    local_redis = aioredis.from_url(redis_url, decode_responses=True)
    
    # 3. Init Engine
    engine = StatefulIndicatorWorker(symbols, local_db, local_redis)
    await engine.warm_up()
    
    print(f"🔧 Worker {shard_id} Ready! Handling {len(symbols)} coins: {symbols[:3]}...", flush=True)
    
    # 4. Subscribe to Redis Stream / PubSub
    # Streamer publishes to 'crypto_updates'
    
    pubsub = local_redis.pubsub()
    await pubsub.subscribe("crypto_updates")
    
    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                # Format from streamer.py: {"s": "BTC/USDT", "k": [ts, o, h, l, c, v]}
                
                symbol = data.get('s')
                k = data.get('k')
                
                if symbol and k and symbol in engine.cache:
                    # k[4] is Close Price, k[5] is Volume
                    price = float(k[4])
                    volume = float(k[5])
                    
                    await engine.process_tick(symbol, price, volume)
                    
            except Exception as e:
                print(f"Error processing msg in Worker {shard_id}: {e}", flush=True)

def run_worker_sync(shard_id, symbols, redis_url, db_dsn):
    """Sync wrapper for asyncio process"""
    asyncio.run(worker_process(shard_id, symbols, redis_url, db_dsn))

async def main():
    print("🚀 Initializing Distributed Indicator Engine v3...", flush=True)
    await main_db.connect()
    
    # 1. Fetch active coins
    rows = await main_db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
    if not rows:
        rows = await main_db.fetch_all("SELECT DISTINCT symbol FROM candles LIMIT 1000")
    
    all_symbols = [r['symbol'] for r in rows]
    total_coins = len(all_symbols)
    
    # 2. Determine Shards
    # Leave 1 core for System/DB, use rest for Workers. Min 1, Max 8.
    cpu_count = multiprocessing.cpu_count()
    num_workers = max(1, min(cpu_count - 1, 8)) 
    
    print(f"📊 Found {total_coins} coins. Spawning {num_workers} workers.", flush=True)
    
    # Split
    chunk_size = len(all_symbols) // num_workers + 1
    chunks = [all_symbols[i:i + chunk_size] for i in range(0, len(all_symbols), chunk_size)]
    
    processes = []
    
    # Config from Env
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    db_dsn = os.environ.get("DATABASE_URL", "") # Passed via env mostly
    
    for i, shard_symbols in enumerate(chunks):
        if not shard_symbols: continue
        
        p = multiprocessing.Process(
            target=run_worker_sync,
            args=(i, shard_symbols, redis_url, db_dsn),
            name=f"IE-Worker-{i}"
        )
        p.start()
        processes.append(p)
        
    print("✅ All workers launched. Engine is running.", flush=True)
    
    # Monitor
    for p in processes:
        p.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
