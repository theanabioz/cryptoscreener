import asyncio
import os
import aiohttp
import logging
from database import db

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

def chunk_list(lst, n):
    """Разбивает список на пачки по n элементов"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def sync_cmc_data():
    if not CMC_API_KEY:
        logger.error("❌ CMC_API_KEY is missing in environment variables")
        return

    logger.info("🚀 Starting CMC Market Cap Sync (Targeted Mode)...")
    await db.connect()
    
    try:
        # 1. Получаем наши символы из БД
        rows = await db.fetch_all("SELECT symbol FROM coin_status")
        
        # Мапа: BTC -> [BTC/USDT, BTC/BTC...]
        # Также подготовим список "чистых" символов для запроса
        base_map = {}
        for r in rows:
            full_symbol = r['symbol']
            base = full_symbol.split('/')[0].upper()
            
            if base not in base_map:
                base_map[base] = []
            base_map[base].append(full_symbol)
            
        all_bases = list(base_map.keys())
        logger.info(f"Loaded {len(all_bases)} unique base assets from DB")

        # Ручной маппинг (Binance -> CMC)
        MANUAL_MAPPING = {
            '1MBABYDOGE': 'BABYDOGE',
            'BTTC': 'BTT',
            'RONIN': 'RON',
            'VELODROME': 'VELO',
            'G': 'GRT', # Часто путают The Graph
            # Автоматическая обработка 1000... будет ниже, но можно и явно
        }

        # Добавим обработку алиасов и "1000" префиксов
        aliases = {}
        for base in all_bases:
            target = None
            
            # 1. Ручной маппинг
            if base in MANUAL_MAPPING:
                target = MANUAL_MAPPING[base]
            
            # 2. Префикс 1000 (если нет ручного)
            elif base.startswith("1000"):
                target = base[4:]
            
            # Если нашли алиас
            if target:
                if target not in base_map: # Если "чистого" тикера у нас нет
                    aliases[target] = base # Запоминаем: CMC(target) -> DB(base)
                    if target not in all_bases:
                        all_bases.append(target) # Добавляем в список для запроса

        # 2. Запрашиваем CMC пачками по 100 символов
        # CMC рекомендует не более 100 символов за раз
        updates = []
        matched_count = 0
        
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            for chunk in chunk_list(all_bases, 20):
                # Фильтруем символы: только латиница и цифры (isascii + isalnum)
                # Это исключит иероглифы и спецсимволы
                valid_chunk = [s for s in chunk if s.isalnum() and s.isascii()]
                if not valid_chunk:
                    continue
                    
                symbols_str = ",".join(valid_chunk)
                params = {
                    'symbol': symbols_str,
                    'convert': 'USD'
                }
                
                async with session.get(CMC_URL, headers=headers, params=params) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"CMC Partial Error {resp.status} for chunk {valid_chunk}: {text}")
                        continue
                    
                    data = await resp.json()
                    results = data.get('data', {})
                    
                    for symbol, coin_obj in results.items():
                        # coin_obj может быть списком (если несколько монет с таким символом)
                        # или словарем (если одна).
                        # API v1 quotes/latest возвращает:
                        # "BTC": { ... }  или "BTC": [ { ... }, { ... } ] ?
                        # Документация говорит: "Returns a mapping of cryptocurrency objects".
                        # Если strict mode выключен (по дефолту), дубликаты могут быть.
                        # Но обычно quotes/latest возвращает `data: { "BTC": [ ... ] }` если duplicate_symbol_detection=true?
                        # В стандартном режиме quotes возвращает ОДИН объект или список?
                        # Проверим тип.
                        
                        target_coin = None
                        
                        if isinstance(coin_obj, list):
                            # Выбираем лучшую монету из списка (с макс капой или рангом)
                            # Сортируем по cmc_rank (чем меньше, тем лучше)
                            # cmc_rank может быть None
                            valid_coins = [c for c in coin_obj if c.get('cmc_rank') is not None]
                            if valid_coins:
                                valid_coins.sort(key=lambda x: x['cmc_rank'])
                                target_coin = valid_coins[0]
                            elif coin_obj:
                                target_coin = coin_obj[0]
                        else:
                            target_coin = coin_obj
                            
                        if target_coin:
                            cap = target_coin['quote']['USD']['market_cap']
                            cmc_id = target_coin['id']
                            
                            if cap:
                                # Находим, кому в нашей базе это принадлежит
                                # Проверяем прямые совпадения
                                if symbol in base_map:
                                    for pair in base_map[symbol]:
                                        updates.append((float(cap), int(cmc_id), pair))
                                        matched_count += 1
                                
                                # Проверяем алиасы (SATS -> 1000SATS)
                                if symbol in aliases:
                                    real_base = aliases[symbol]
                                    if real_base in base_map:
                                        for pair in base_map[real_base]:
                                            updates.append((float(cap), int(cmc_id), pair))
                                            matched_count += 1

                # Пауза между чанками
                await asyncio.sleep(1)

        logger.info(f"Matched {matched_count} pairs. Preparing {len(updates)} updates...")
        
        if updates:
            query = "UPDATE coin_status SET market_cap = $1, cmc_id = $2 WHERE symbol = $3"
            async with db.pool.acquire() as conn:
                await conn.executemany(query, updates)
            logger.info("✅ Database updated successfully")
            
    except Exception as e:
        logger.error(f"Error during CMC sync: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(sync_cmc_data())