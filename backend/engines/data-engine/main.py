import asyncio
import sys
import os
import json
import ccxt.pro as ccxt_pro
from datetime import datetime, timezone

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

async def run_streamer():
    """Слушает живые котировки Binance и пушит в Redis/DB."""
    print("🚀 Data Engine: Streamer started", flush=True)
    
    exchange = ccxt_pro.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    queue = asyncio.Queue()

    # Внутренний воркер для записи в БД (пакетный режим)
    async def db_writer():
        batch_size = 500
        buffer = []
        while True:
            item = await queue.get()
            buffer.append(item)
            try:
                while len(buffer) < batch_size:
                    buffer.append(queue.get_nowait())
            except asyncio.QueueEmpty: pass
            
            if buffer:
                records = []
                for symbol, c in buffer:
                    dt = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                    records.append((dt, symbol, c[1], c[2], c[3], c[4], c[5]))
                
                try:
                    query = """
                        INSERT INTO candles (time, symbol, open, high, low, close, volume)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (time, symbol) DO UPDATE SET
                            high = GREATEST(candles.high, EXCLUDED.high),
                            low = LEAST(candles.low, EXCLUDED.low),
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume;
                    """
                    async with db.pool.acquire() as conn:
                        await conn.executemany(query, records)
                except Exception as e:
                    print(f"  [!] DB Write Error: {e}", flush=True)
                buffer.clear()
            await asyncio.sleep(1)

    asyncio.create_task(db_writer())

    while True:
        try:
            tickers = await exchange.watch_tickers()
            if tickers:
                for symbol, ticker in tickers.items():
                    if not symbol.endswith('/USDT'): continue
                    
                    # Формируем данные для Redis и БД
                    # ВАЖНО: ticker['open'] в Binance - это открытие за 24 часа.
                    # Для 1м свечи мы используем текущую цену (last) как базу.
                    timestamp = ticker['timestamp'] or int(datetime.now().timestamp() * 1000)
                    current_price = ticker['last']
                    
                    # Для новой свечи в этой минуте OHLC изначально равны текущей цене
                    candle = [
                        timestamp,
                        current_price, # open
                        current_price, # high
                        current_price, # low
                        current_price, # close
                        ticker['baseVolume']
                    ]

                    # 1. Мгновенный пуш в Redis для WebSockets
                    if db.redis:
                        await db.redis.publish("crypto_updates", json.dumps({"s": symbol, "k": candle}))

                    # 2. В очередь для записи в БД
                    await queue.put((symbol, candle))
        except Exception as e:
            print(f"❌ Streamer Error: {e}", flush=True)
            await asyncio.sleep(5)

async def main():
    await db.connect()
    await run_streamer()

if __name__ == "__main__":
    asyncio.run(main())
