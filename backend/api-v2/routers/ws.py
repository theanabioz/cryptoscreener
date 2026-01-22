from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import logging
import asyncio
from database import db

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        # Отправляем сообщение всем подключенным клиентам
        # Используем копию списка, так как он может измениться во время итерации
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                # Если отправка не удалась (клиент отвалился), удаляем его
                # Обычно WebSocketDisconnect ловится в эндпоинте, но это страховка
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Просто поддерживаем соединение.
            # В будущем здесь можно обрабатывать команды от клиента (например, подписка на конкретные пары)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS Error: {e}")
        manager.disconnect(websocket)

async def start_redis_listener():
    """
    Фоновая задача: слушает Redis и пересылает сообщения в WebSockets
    """
    print("Attempting to start Redis listener...", flush=True)
    if not db.redis:
        print("❌ Redis not initialized in db object, WS listener cannot start", flush=True)
        return
        
    try:
        pubsub = db.redis.pubsub()
        await pubsub.subscribe("crypto_updates")
        print("🎧 Redis -> WebSocket bridge started and subscribed to 'crypto_updates'", flush=True)
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                # print(f"Bridge received: {message['data'][:50]}...", flush=True)
                await manager.broadcast(message["data"])
    except Exception as e:
        print(f"❌ Redis listener crashed: {e}", flush=True)
    finally:
        print("🛑 Redis listener stopped", flush=True)


