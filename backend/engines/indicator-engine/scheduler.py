import asyncio
import sys
import os
import time

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: High-Frequency Scheduler started", flush=True)
    await db.connect()
    
    try:
        await db.redis.xgroup_create("ta_tasks", "beast_group", id="0", mkstream=True)
    except: pass

    while True:
        start_time = time.time()
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        
        if symbols:
            # Очищаем старые «зависшие» сообщения, если они есть
            try:
                await db.redis.xtrim("ta_tasks", minid=9999999999999)
            except: pass
            
            for s in symbols:
                await db.redis.xadd("ta_tasks", {"symbol": s['symbol']})
            
            print(f"📡 [BATCH START] Dispatched {len(symbols)} tasks at {time.strftime('%H:%M:%S')}", flush=True)
            
            # Ждем завершения
            while True:
                q_len = await db.redis.xlen("ta_tasks")
                if q_len == 0:
                    break
                # Проверяем чаще для 5 воркеров
                await asyncio.sleep(1)
            
            duration = time.time() - start_time
            print(f"🏁 [BATCH FINISHED] Cycle time: {duration:.2f}s. Restarting in 5s...", flush=True)
            
        await asyncio.sleep(5) # Минимальная пауза между кругами

if __name__ == "__main__":
    asyncio.run(run_scheduler())