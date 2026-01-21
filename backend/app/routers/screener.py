from fastapi import APIRouter, HTTPException, Query
from database import db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/coins")
async def get_coins(ids: str = None):
    """
    Возвращает список монет из таблицы coin_status (предварительно рассчитанные данные).
    """
    
    # Теперь запрос очень простой и быстрый
    query = """
        SELECT 
            symbol,
            current_price,
            volume_24h, -- Пока это volume за 1h, исправим в воркере позже
            rsi_14,
            macd,
            price_change_24h -- Это поле мы пока не заполнили в воркере, надо добавить
        FROM coin_status
    """
    
    # Временно: чтобы не ломать фронтенд, пока воркер не заполнил базу,
    # сделаем fallback на старый метод, если таблица пустая?
    # Нет, лучше запустить воркер.
    
    # Давайте пока оставим старый метод, НО подмешаем туда RSI из coin_status через JOIN
    
    query = """
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
            cs.rsi_14,
            cs.macd,
            cs.ema_50
        FROM latest_data ld
        LEFT JOIN coin_status cs ON ld.symbol = cs.symbol
    """
    
    try:
        rows = await db.fetch_all(query)
        
        result = []
        for row in rows:
            price = row['current_price']
            open_24h = row['open_24h']
            change_pct = ((price - open_24h) / open_24h * 100) if open_24h else 0
            
            result.append({
                "id": row['symbol'].replace('/', '').lower(),
                "symbol": row['symbol'].split('/')[0],
                "name": row['symbol'].split('/')[0],
                "image": f"https://assets.coincap.io/assets/icons/{row['symbol'].split('/')[0].lower()}@2x.png",
                "current_price": price,
                "price_change_percentage_24h": round(change_pct, 2),
                "market_cap": 0,
                "total_volume": row['volume_24h'] or 0,
                "rsi": row['rsi_14'] or 50.0, # Берем реальный RSI или 50
                "macd": row['macd'] or 0
            })
            
        return result

    except Exception as e:
        print(f"Error fetching coins: {e}")
        # Если таблицы coin_status нет, вернем ошибку 500, но это ок для дебага
        raise HTTPException(status_code=500, detail=str(e))
