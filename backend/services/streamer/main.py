import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timezone

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from common.database import db
import websockets

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger("Streamer")

async def db_writer(queue):
    """Batched DB writer"""
    batch = []
    while True:
        try:
            # Wait for first item
            item = await queue.get()
            batch.append(item)
            
            # Drain
            try:
                while not queue.empty() and len(batch) < 2000:
                    batch.append(queue.get_nowait())
            except: pass
            
            if batch:
                try:
                    query = """
                        INSERT INTO candles (time, symbol, open, high, low, close, volume)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (time, symbol) DO UPDATE SET
                            high = GREATEST(candles.high, EXCLUDED.high),
                            low = LEAST(candles.low, EXCLUDED.low),
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                    """
                    async with db.pool.acquire() as conn:
                        await conn.executemany(query, batch)
                except Exception as e:
                    logger.error(f"DB Write Error: {e}")
                
                batch = []
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Writer Loop Error: {e}")
            await asyncio.sleep(1)

async def run():
    await db.connect()
    queue = asyncio.Queue()
    asyncio.create_task(db_writer(queue))
    
    url = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
    
    while True:
        try:
            async with websockets.connect(url) as ws:
                logger.info("🚀 Connected to Binance")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    
                    pipeline = db.redis.pipeline()
                    
                    for t in data:
                        s = t['s']
                        if not s.endswith('USDT'): continue
                        
                        symbol = f"{s[:-4]}/USDT"
                        price = float(t['c'])
                        vol = float(t['v'])
                        ts_ms = t['E']
                        
                        # PubSub for Engines/UI
                        payload = {
                            "s": symbol,
                            "p": price,
                            "v": vol,
                            "t": ts_ms
                        }
                        pipeline.publish("crypto_ticks", json.dumps(payload))
                        
                        # DB Record
                        dt = datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc)
                        record = (dt, symbol, float(t['o']), float(t['h']), float(t['l']), price, vol)
                        queue.put_nowait(record)
                        
                    await pipeline.execute()
                    
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run())
