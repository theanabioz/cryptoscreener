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
    if not db.redis:
        logger.error("❌ Redis not initialized, WS listener cannot start")
        return
        
    pubsub = db.redis.pubsub()
    await pubsub.subscribe("crypto_updates")
    logger.info("🎧 Redis -> WebSocket bridge started")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # message['data'] - это JSON строка от streamer.py
                await manager.broadcast(message["data"])
    except Exception as e:
        logger.error(f"❌ Redis listener crashed: {e}")
    finally:
        await pubsub.close()
