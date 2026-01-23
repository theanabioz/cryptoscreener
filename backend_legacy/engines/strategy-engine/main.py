import asyncio
import sys
import os
import json

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def check_strategies():
    """Проверка стратегий на базе данных из JSONB (The Beast v3.3)."""
    try:
        # ЗАПРОС БЕЗ rsi_14
        query = "SELECT symbol, indicators_1h, current_price, volume_24h FROM coin_status"
        rows = await db.fetch_all(query)
        
        for r in rows:
            inds = r['indicators_1h'] or {}
            # Безопасно достаем значения из JSONB
            rsi = inds.get('RSI_14')
            
            if rsi is None: continue

            # Пример стратегии: RSI Перепроданность
            if float(rsi) < 30:
                print(f"🔥 [STRATEGY] {r['symbol']} is OVERSOLD (RSI: {rsi})", flush=True)
    except Exception as e:
        print(f"❌ Strategy Error: {e}", flush=True)

async def main():
    print("🚀 Strategy Engine v3.3 (JSONB Mode) started", flush=True)
    await db.connect()
    while True:
        await check_strategies() # Теперь имя совпадает
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())