import asyncio
import sys
import os
import aiohttp
import json
import logging

# Импорты из common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_telegram_message(chat_id, text):
    """Отправляет сообщение пользователю через Bot API."""
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to send message to {chat_id}: {await resp.text()}")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

async def handle_bot_updates():
    """Слушает входящие сообщения бота (для регистрации пользователей)."""
    offset = 0
    print("🤖 Notification Engine: Bot updates listener started", flush=True)
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for update in data.get("result", []):
                            offset = update["update_id"] + 1
                            message = update.get("message", {})
                            chat_id = message.get("chat", {}).get("id")
                            text = message.get("text", "")
                            username = message.get("from", {}).get("username", "unknown")

                            if text == "/start":
                                # Регистрируем пользователя
                                query = "INSERT INTO bot_users (chat_id, username) VALUES ($1, $2) ON CONFLICT (chat_id) DO NOTHING"
                                await db.execute(query, chat_id, username)
                                await send_telegram_message(chat_id, "🚀 <b>Welcome to Crypto Screener!</b>\nYou will now receive real-time alerts about market opportunities.")
                                print(f"✅ New user registered: {username} ({chat_id})", flush=True)
        except Exception as e:
            logger.error(f"Bot updates error: {e}")
        await asyncio.sleep(1)

async def poll_signals():
    """Опрашивает таблицу сигналов и рассылает уведомления."""
    last_signal_id = 0
    # Инициализируем last_signal_id текущим максимумом, чтобы не слать старье
    try:
        res = await db.fetch_all("SELECT MAX(id) as max_id FROM signals")
        if res and res[0]['max_id']:
            last_signal_id = res[0]['max_id']
    except: pass

    print("📢 Notification Engine: Signals poller started", flush=True)
    
    while True:
        try:
            # Ищем новые сигналы
            query = "SELECT id, symbol, type, value, time FROM signals WHERE id > $1 ORDER BY id ASC"
            new_signals = await db.fetch_all(query, last_signal_id)
            
            if new_signals:
                # Получаем всех подписчиков
                users = await db.fetch_all("SELECT chat_id FROM bot_users")
                
                for sig in new_signals:
                    last_signal_id = sig['id']
                    emoji = "🟢" if "OVERSOLD" in sig['type'] else "🔴"
                    msg = f"{emoji} <b>SIGNAL: {sig['type']}</b>\n\n" \
                          f"Asset: <code>{sig['symbol']}</code>\n" \
                          f"Value: <b>{sig['value']}</b>\n" \
                          f"Time: {sig['time'].strftime('%H:%M:%S')}"
                    
                    for user in users:
                        await send_telegram_message(user['chat_id'], msg)
                        await asyncio.sleep(0.05) # Защита от спам-фильтра TG
            
        except Exception as e:
            logger.error(f"Poll signals error: {e}")
        await asyncio.sleep(10) # Проверка новых сигналов каждые 10 сек

async def main():
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!", flush=True)
        return

    await db.connect()
    # Запускаем две параллельные задачи
    await asyncio.gather(
        handle_bot_updates(),
        poll_signals()
    )

if __name__ == "__main__":
    asyncio.run(main())