from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from common.database import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.connect()

@app.get("/api/coins")
async def get_coins():
    q = "SELECT symbol, current_price, indicators_1m, indicators_1h FROM coin_status ORDER BY symbol"
    rows = await db.fetch_all(q)
    
    res = []
    for r in rows:
        d = dict(r)
        # Parse JSON if string
        for k in ['indicators_1m', 'indicators_1h']:
            if isinstance(d[k], str):
                d[k] = json.loads(d[k])
        res.append(d)
    return res

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = db.redis.pubsub()
    await pubsub.subscribe("crypto_ticks")
    
    try:
        async for msg in pubsub.listen():
            if msg['type'] == 'message':
                await websocket.send_text(msg['data'])
    except:
        pass
