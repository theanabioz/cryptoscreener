import asyncio
import sys
import os
import json

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def check_strategies():
    """Простейшая проверка стратегий на базе данных из JSONB."""
    # Берем индикаторы из indicators_1h
    query = "SELECT symbol, indicators_1h, current_price, volume_24h FROM coin_status"
    rows = await db.fetch_all(query)
    
    for r in rows:
        inds = r['indicators_1h'] or {}
        # Безопасно достаем значения
        rsi = inds.get('RSI_14')
        ema_50 = inds.get('EMA_50')
        
        if rsi is None or ema_50 is None: continue

        # Пример стратегии: RSI Перепроданность
        if float(rsi) < 30:
            print(f"🔥 [STRATEGY] {r['symbol']} is OVERSOLD (RSI: {rsi})", flush=True)
            # Тут будет отправка в Redis для бота


async def main():
    await db.connect()
    while True:
        await scan_strategies()
        await asyncio.sleep(60) # Проверка раз в минуту

if __name__ == "__main__":
    asyncio.run(main())
