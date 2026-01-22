import asyncio
import os
import aiohttp
import logging
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

async def sync_cmc_data():
    if not CMC_API_KEY:
        logger.error("❌ CMC_API_KEY is missing in environment variables")
        return

    logger.info("🚀 Starting CMC Market Cap Sync...")
    await db.connect()
    
    try:
        # 1. Получаем наши символы из БД (для проверки)
        # Нам нужно знать, какие монеты у нас есть, чтобы обновлять только их (хотя UPDATE where symbol in (...) сделает это сам)
        # Но для логов полезно знать охват.
        rows = await db.fetch_all("SELECT symbol FROM coin_status")
        # Создаем мапу: BTC -> [BTC/USDT, BTC/BTC...]
        my_map = {}
        for r in rows:
            base = r['symbol'].split('/')[0].upper()
            if base not in my_map:
                my_map[base] = []
            my_map[base].append(r['symbol'])
            
        logger.info(f"Loaded {len(my_map)} unique base assets from DB")

        # 2. Запрашиваем CMC (Топ 3000)
        # Стоимость: 1 + 15 = 16 кредитов. Раз в 2 часа = 192 кредита/день (из 333).
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'start': '1',
            'limit': '3000', # Увеличили охват
            'convert': 'USD'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(CMC_URL, headers=headers, params=params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"CMC API Error {resp.status}: {text}")
                    return
                
                data = await resp.json()
                coins = data.get('data', [])
                logger.info(f"Fetched {len(coins)} coins from CMC")

        # 3. Сопоставление и обновление
        updates = []
        matched_count = 0
        
        # Создаем индекс символов CMC для быстрого поиска
        # Некоторые монеты могут иметь одинаковые символы, но разные ранги. 
        # CMC отдает в порядке ранга, поэтому берем первую (самую крупную) монету с таким символом.
        cmc_map = {}
        for coin in coins:
            s = coin['symbol'].upper()
            if s not in cmc_map:
                cmc_map[s] = coin['quote']['USD']['market_cap']

        for base_asset, pairs in my_map.items():
            cap = None
            
            # 1. Прямое совпадение
            if base_asset in cmc_map:
                cap = cmc_map[base_asset]
            
            # 2. Попытка убрать префикс 1000 (1000SATS -> SATS)
            elif base_asset.startswith('1000') and base_asset[4:] in cmc_map:
                cap = cmc_map[base_asset[4:]]
                
            # 3. Другие частные случаи можно добавить тут
            
            if cap is not None:
                matched_count += 1
                for pair in pairs:
                    updates.append((float(cap), pair))
        
        logger.info(f"Matched {matched_count} base assets. Preparing {len(updates)} updates...")
        
        if updates:
            # Batch update
            query = "UPDATE coin_status SET market_cap = $1 WHERE symbol = $2"
            async with db.pool.acquire() as conn:
                await conn.executemany(query, updates)
            logger.info("✅ Database updated successfully")
            
    except Exception as e:
        logger.error(f"Error during CMC sync: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(sync_cmc_data())
