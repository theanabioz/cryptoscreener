import asyncio
import sys
import os

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_notification_engine():
    print("🚀 Notification Engine: Started", flush=True)
    await db.connect()
    
    # В будущем здесь будет цикл обработки алертов из очереди Redis
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_notification_engine())
