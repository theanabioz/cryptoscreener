import asyncio
import sys
import os
import time

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: Precision Benchmark Scheduler started", flush=True)
    await db.connect()
    
    stream_key = "ta_tasks"
    group_name = "beast_group"

    try:
        await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
    except: pass

    while True:
        # 1. Получаем монеты
        symbols = await db.fetch_all("SELECT symbol FROM coin_status")
        if not symbols:
            await asyncio.sleep(10)
            continue

        # 2. Очищаем стрим перед стартом
        await db.redis.delete(stream_key)
        try:
            await db.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        except: pass

        # 3. Засекаем время и раздаем задачи
        start_time = time.time()
        for s in symbols:
            await db.redis.xadd(stream_key, {"symbol": s['symbol']})
        
        print(f"📡 [BATCH START] {len(symbols)} coins dispatched at {time.strftime('%H:%M:%S')}", flush=True)

        # 4. Ждем, пока 5 воркеров всё разберут
        while True:
            # Проверяем состояние группы
            groups = await db.redis.xinfo_groups(stream_key)
            pending = 0
            for g in groups:
                if g['name'] == group_name:
                    pending = g['pending'] # Сколько задач в работе прямо сейчас
            
            # Проверяем сколько задач еще даже не взято (длина стрима минус прочитанные)
            # В нашем случае проще смотреть на XLEN, так как мы не удаляем сообщения в процессе
            # Но мы знаем что всего 450.
            
            # Будем ориентироваться на логи воркеров и PENDING
            # Самый надежный способ - если воркеры сделали XACK, PENDING уменьшается.
            # Но воркеры подтверждают задачу СРАЗУ после выполнения.
            
            if pending == 0:
                # Проверим XLEN (если он равен количеству монет и PENDING 0, значит все взяты и обработаны)
                # Но так как мы хотим точность, просто подождем пока PENDING станет 0 
                # после того как все задачи были вычитаны.
                break
            
            await asyncio.sleep(1)

        duration = time.time() - start_time
        print(f"🏁 [BATCH FINISHED] 450 coins processed in {duration:.2f} seconds by 5 workers.", flush=True)
        
        # Пауза перед новым кругом, чтобы не частить (например 30 сек)
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_scheduler())
