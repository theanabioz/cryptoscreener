from fastapi import APIRouter, HTTPException, Query
from common.database import db
from datetime import datetime, timedelta

router = APIRouter()

import json

@router.get("/coins")
async def get_coins(ids: str = None, strategy: str = None):
    """
    Возвращает список монет из таблицы coin_status.
    Поддерживает фильтрацию по стратегиям.
    """
    
    # Базовый запрос
    # Данные теперь тянем из JSONB поля indicators_1h
    query_base = """
        WITH latest_data AS (
            SELECT 
                symbol,
                LAST(close, time) as current_price,
                FIRST(close, time) as open_24h,
                SUM(volume) as volume_24h
            FROM candles
            WHERE time > NOW() - INTERVAL '24 hours'
            GROUP BY symbol
        )
        SELECT 
            ld.*,
            cs.indicators_1h,
            cs.market_cap,
            cs.cmc_id,
            cs.sparkline_in_7d
        FROM latest_data ld
        LEFT JOIN coin_status cs ON ld.symbol = cs.symbol
        WHERE 1=1
        ORDER BY cs.market_cap DESC NULLS LAST
    """
    
    params = []
    
    # Фильтрация по стратегии (теперь через JSONB)
    if strategy == 'rsi-oversold':
        query_base += " AND (cs.indicators_1h->>'RSI_14')::float < 30"
    elif strategy == 'strong-trend':
        query_base += " AND ld.current_price > (cs.indicators_1h->>'EMA_50')::float"
    elif strategy == 'pump-radar':
        query_base += " AND ld.volume_24h > 50000000" 

    try:
        rows = await db.fetch_all(query_base)
        
        result = []
        for row in rows:
            price = row['current_price']
            open_24h = row['open_24h']
            change_pct = ((price - open_24h) / open_24h * 100) if open_24h else 0
            
            # Извлекаем индикаторы из JSONB
            inds = row['indicators_1h'] or {}
            
            # В pandas-ta ключи обычно в верхнем регистре или имеют специфические имена
            # Пытаемся найти RSI_14 (или rsi_14 в зависимости от версии)
            rsi = inds.get('RSI_14') or inds.get('rsi_14')
            macd = inds.get('MACD_12_26_9') or inds.get('macd')
            macd_s = inds.get('MACDs_12_26_9') or inds.get('macd_signal')
            ema50 = inds.get('EMA_50') or inds.get('ema_50')
            bb_u = inds.get('BBU_20_2.0') or inds.get('bb_upper')
            bb_l = inds.get('BBL_20_2.0') or inds.get('bb_lower')

            # Картинка
            image_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{row['cmc_id'] or 1}.png"
            
            # Спарклайн
            sparkline_final = {"price": []}
            if row['sparkline_in_7d']:
                try:
                    val = row['sparkline_in_7d']
                    if isinstance(val, str): val = json.loads(val)
                    if isinstance(val, dict) and "price" in val: sparkline_final = val
                except: pass

            result.append({
                "id": row['symbol'].replace('/', '').lower(),
                "symbol": row['symbol'].split('/')[0],
                "name": row['symbol'].split('/')[0],
                "image": image_url,
                "current_price": price,
                "price_change_percentage_24h": round(change_pct, 2),
                "market_cap": row['market_cap'] or 0,
                "total_volume": row['volume_24h'] or 0,
                "rsi": round(float(rsi), 2) if rsi is not None else 50.0, 
                "macd": round(float(macd), 2) if macd is not None else 0,
                "macd_signal": round(float(macd_s), 2) if macd_s is not None else 0,
                "ema50": float(ema50) if ema50 is not None else None,
                "bb_upper": float(bb_u) if bb_u is not None else None,
                "bb_lower": float(bb_l) if bb_l is not None else None,
                "sparkline_in_7d": sparkline_final
            })
            
        return result

    except Exception as e:
        print(f"Error fetching coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))
