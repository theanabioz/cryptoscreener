import asyncio
import time
import sys
import os

# Добавляем путь к common, чтобы импорты работали
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_scheduler():
    print("🚀 Indicator Engine: Scheduler started", flush=True)
    await db.connect()
    
    while True:
        try:
            start_time = time.time()
            
            # 1. Получаем список активных монет
            rows = await db.fetch_all("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
            symbols = [r['symbol'] for r in rows]
            
            if not symbols:
                print("⚠️ No symbols to process. Waiting...", flush=True)
            else:
                # 2. Кидаем задачи в Redis Stream 'ta_tasks'
                # Поток (Stream) в Redis — это идеальная очередь для распределенных систем
                if db.redis:
                    for symbol in symbols:
                        # Формат задачи: id=*, symbol=...
                        await db.redis.xadd("ta_tasks", {"symbol": symbol}, maxlen=1000)
                    
                    print(f"📡 Dispatched {len(symbols)} tasks to Redis Streams", flush=True)
            
            # Раз в минуту — оптимально для часовых индикаторов
            elapsed = time.time() - start_time
            await asyncio.sleep(max(60 - elapsed, 10))
            
        except Exception as e:
            print(f"❌ Scheduler Error: {e}", flush=True)
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_scheduler())
