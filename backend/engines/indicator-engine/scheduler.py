import asyncio
import sys
import os
import time

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: Professional Scheduler started", flush=True)
    await db.connect()
    
    stream_key = "ta_tasks"
    group_name = "beast_group"

    # Создаем группу один раз при старте
    try:
        await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
    except: pass

    while True:
        start_time = time.time()
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        
        if symbols:
            # Добавляем задачи в стрим с ограничением длины (чтобы не переполнять Redis)
            for s in symbols:
                await db.redis.xadd(stream_key, {"symbol": s['symbol']}, maxlen=1000, approximate=True)
            
            print(f"📡 [BATCH] Dispatched {len(symbols)} tasks. Total market update started.", flush=True)
            
        # Нам не нужно ждать здесь. Воркеры сами разберут задачи.
        # Мы просто закидываем новую порцию задач каждую минуту.
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_scheduler())