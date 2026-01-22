import asyncio
import aiohttp
import logging
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def update_caps():
    logger.info("🚀 Starting Market Cap Update...")
    await db.connect()
    
    try:
        # 1. Получаем наши символы из БД
        rows = await db.fetch_all("SELECT symbol FROM coin_status")
        # Создаем мапу: BTC -> BTC/USDT (для простого матчинга)
        # Если есть дубли (BTC/USDT, BTC/BTC), это может быть проблемой, но у нас в основном USDT
        my_map = {}
        for r in rows:
            base = r['symbol'].split('/')[0].upper()
            if r['symbol'].endswith('/USDT'): # Приоритет USDT парам
                my_map[base] = r['symbol']
        
        logger.info(f"Loaded {len(my_map)} symbols from DB")

        # 2. Запрашиваем CoinGecko
        # Берем топ 500 монет, это покроет большинство наших пар
        async with aiohttp.ClientSession() as session:
            all_data = []
            for page in [1, 2]:
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "page": page,
                    "sparkline": "false"
                }
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        all_data.extend(data)
                        logger.info(f"Fetched page {page}: {len(data)} coins")
                    else:
                        logger.error(f"Failed to fetch page {page}: {resp.status}")
                    
                    # Пауза чтобы не бить лимиты
                    await asyncio.sleep(2)

        # 3. Сопоставление и обновление
        updates = []
        for coin in all_data:
            symbol = coin['symbol'].upper()
            cap = coin['market_cap']
            
            if symbol in my_map and cap is not None:
                full_symbol = my_map[symbol]
                updates.append((float(cap), full_symbol))
        
        logger.info(f"Ready to update {len(updates)} coins with Market Cap data")
        
        if updates:
            query = "UPDATE coin_status SET market_cap = $1 WHERE symbol = $2"
            async with db.pool.acquire() as conn:
                await conn.executemany(query, updates)
            logger.info("✅ Database updated successfully")
            
    except Exception as e:
        logger.error(f"Error during update: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(update_caps())
