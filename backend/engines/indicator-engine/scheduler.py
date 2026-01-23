import asyncio
import sys
import os
import time

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: High-Reliability Scheduler started", flush=True)
    await db.connect()
    
    stream_key = "ta_tasks"
    group_name = "beast_group"

    # Гарантируем наличие группы
    try:
        await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
    except: pass

    while True:
        start_time = time.time()
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        
        if symbols:
            # Используем PIPELINE для мгновенной отправки 450 задач
            async with db.redis.pipeline(transaction=False) as pipe:
                for s in symbols:
                    pipe.xadd(stream_key, {"symbol": s['symbol']}, maxlen=1000, approximate=True)
                await pipe.execute()
            
            print(f"📡 [DISPATCH] {len(symbols)} coins sent to stream at {time.strftime('%H:%M:%S')}", flush=True)
            
        # Просто ждем 60 секунд до следующего круга. 
        # Воркеры (8 штук) гарантированно разберут 450 задач за это время.
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_scheduler())