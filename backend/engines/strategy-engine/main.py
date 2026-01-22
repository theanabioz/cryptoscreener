import asyncio
import sys
import os
import json

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def scan_strategies():
    """Сканирует монеты на выполнение условий торговых стратегий."""
    print("🚀 Strategy Engine: Scanning for opportunities...", flush=True)
    
    try:
        # Получаем актуальные данные из coin_status
        query = "SELECT symbol, rsi_14, current_price, ema_50, volume_24h FROM coin_status"
        rows = await db.fetch_all(query)
        
        signals = []
        for r in rows:
            symbol = r['symbol']
            rsi = r['rsi_14']
            price = r['current_price']
            ema50 = r['ema_50']
            
            # --- СТРАТЕГИЯ 1: RSI Oversold ---
            if rsi and rsi < 30:
                signals.append((symbol, 'RSI_OVERSOLD', str(round(rsi, 2))))
            
            # --- СТРАТЕГИЯ 2: Strong Trend (Price > EMA50) ---
            if price and ema50 and price > ema50:
                # Генерируем сигнал только если это пересечение (в будущем)
                # Пока просто помечаем трендовые
                pass

            # --- СТРАТЕГИЯ 3: Pump Radar (Volume spike) ---
            # Здесь нужна история, пока пропустим для простоты

        if signals:
            print(f"  [+] Found {len(signals)} signals. Saving...", flush=True)
            # Записываем сигналы в БД
            query_insert = "INSERT INTO signals (symbol, type, value) VALUES ($1, $2, $3)"
            async with db.pool.acquire() as conn:
                await conn.executemany(query_insert, signals)
                
    except Exception as e:
        print(f"❌ Strategy Error: {e}", flush=True)

async def main():
    await db.connect()
    while True:
        await scan_strategies()
        await asyncio.sleep(60) # Проверка раз в минуту

if __name__ == "__main__":
    asyncio.run(main())
