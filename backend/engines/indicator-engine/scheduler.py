import asyncio
import sys
import os
import time

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: Scheduler with Benchmark started", flush=True)
    await db.connect()
    
    while True:
        start_time = time.time()
        
        # Получаем список всех символов
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        
        if symbols:
            # Очищаем старую очередь (если воркеры не успели)
            # Это важно, чтобы задачи не копились бесконечно
            await db.redis.delete("ta_tasks")
            
            for s in symbols:
                await db.redis.xadd("ta_tasks", {"symbol": s['symbol']})
            
            print(f"📡 [BATCH START] Dispatched {len(symbols)} tasks at {time.strftime('%H:%M:%S')}", flush=True)
            
            # Ждем, пока воркеры разберут очередь
            while True:
                q_len = await db.redis.xlen("ta_tasks")
                if q_len == 0:
                    break
                await asyncio.sleep(1) # Проверка каждую секунду
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"🏁 [BATCH FINISHED] 450 coins processed in {duration:.2f} seconds.", flush=True)
            
        await asyncio.sleep(10) # Пауза перед новым кругом

if __name__ == "__main__":
    asyncio.run(run_scheduler())