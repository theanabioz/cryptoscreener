import asyncio
import sys
import os
import multiprocessing
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from common.database import db
from worker import start_worker

async def main():
    print("🚀 Indicator Engine Manager v4")
    await db.connect()
    
    # Wait for data
    while True:
        rows = await db.fetch_all("SELECT DISTINCT symbol FROM candles")
        if rows:
            break
        print("Waiting for candle data...")
        await asyncio.sleep(5)
        
    symbols = [r['symbol'] for r in rows]
    
    # Init Status Table
    batch = [(s,) for s in symbols]
    async with db.pool.acquire() as conn:
        await conn.executemany("INSERT INTO coin_status (symbol) VALUES ($1) ON CONFLICT DO NOTHING", batch)
    
    print(f"✅ Loaded {len(symbols)} symbols.")
    
    # Launch Workers
    cpu = multiprocessing.cpu_count()
    num_workers = min(cpu, 8)
    chunk_size = len(symbols) // num_workers + 1
    chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]
    
    processes = []
    for i, chunk in enumerate(chunks):
        if not chunk: continue
        p = multiprocessing.Process(target=start_worker, args=(i, chunk))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

if __name__ == "__main__":
    asyncio.run(main())
