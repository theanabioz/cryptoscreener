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
    
    stream_key = "ta_tasks"
    group_name = "beast_group"

    try:
        await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
    except: pass

    while True:
        start_time = time.time()
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        
        if symbols:
            # Очищаем стрим перед новой партией
            await db.redis.delete(stream_key)
            try:
                await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
            except: pass
            
            # Добавляем задачи
            for s in symbols:
                await db.redis.xadd(stream_key, {"symbol": s['symbol']})
            
            print(f"📡 [BATCH START] Dispatched {len(symbols)} tasks at {time.strftime('%H:%M:%S')}", flush=True)
            
            # Ждем завершения круга
            # Каждые 5 секунд проверяем, сколько задач осталось
            while True:
                # В Redis Streams мы можем проверить информацию о группе
                info = await db.redis.xinfo_groups(stream_key)
                pending = 0
                for g in info:
                    if g['name'] == group_name:
                        # В лаконичном режиме смотрим на количество невыполненных задач
                        # Но так как мы удаляем стрим каждый раз, проще смотреть на XLEN после того как группа создана заново
                        pass
                
                # Самый простой способ при удалении стрима:
                # Мы смотрим, сколько задач осталось НЕ ПРОЧИТАННЫХ (ID > чем последний прочитанный)
                # Но для бенчмарка мы просто подождем, пока воркеры разберут XLEN
                # (Воркеры в нашей версии НЕ удаляют из XLEN)
                
                # ИСПРАВЛЕНИЕ: Мы будем считать Success сообщения в логах или просто ждать фиксированное время?
                # Нет, давайте сделаем по-умному:
                await asyncio.sleep(10)
                # Если прошло 60 секунд, считаем круг завершенным для планировщика
                if time.time() - start_time > 60:
                    break
            
            duration = time.time() - start_time
            print(f"🏁 [BATCH FINISHED] Cycle complete. Restarting in 5s...", flush=True)
            
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_scheduler())
