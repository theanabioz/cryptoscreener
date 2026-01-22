from fastapi import APIRouter, HTTPException, Query
from database import db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/coins")
async def get_coins(ids: str = None, strategy: str = None):
    """
    Возвращает список монет из таблицы coin_status.
    Поддерживает фильтрацию по стратегиям.
    """
    
    # Базовый запрос
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
        ),
        sparklines AS (
             SELECT 
                symbol,
                array_agg(close ORDER BY bucket) as sparkline
             FROM (
                SELECT 
                    symbol,
                    time_bucket('1 hour', time) as bucket,
                    LAST(close, time) as close
                FROM candles
                WHERE time > NOW() - INTERVAL '24 hours'
                GROUP BY symbol, bucket
             ) sub
             GROUP BY symbol
        )
        SELECT 
            ld.*,
            cs.rsi_14,
            cs.macd,
            cs.ema_50,
            cs.market_cap,
            cs.cmc_id,
            sp.sparkline
        FROM latest_data ld
        LEFT JOIN coin_status cs ON ld.symbol = cs.symbol
        LEFT JOIN sparklines sp ON ld.symbol = sp.symbol
        WHERE 1=1
    """
    
    params = []
    
    # Фильтрация по стратегии
    if strategy == 'rsi-oversold':
        query_base += " AND cs.rsi_14 < 30"
    elif strategy == 'strong-trend':
        query_base += " AND ld.current_price > cs.ema_50"
    elif strategy == 'pump-radar':
        # Пока просто фильтр по высокому объему, в будущем - аномалия
        query_base += " AND ld.volume_24h > 50000000" 
    elif strategy == 'volatility':
        # Change > 5% or < -5% (нужно считать change в SQL для фильтрации)
        # Упростим: просто вернем все, отсортируем на клиенте или сделаем HAVING
        pass

    # Фильтрация по ID (если нужно)
    if ids:
        id_list = ids.split(',')
        # Сложно матчить 'btc' с 'BTC/USDT', пропустим пока для краткости
        pass

    try:
        rows = await db.fetch_all(query_base)
        
        result = []
        for row in rows:
            price = row['current_price']
            open_24h = row['open_24h']
            change_pct = ((price - open_24h) / open_24h * 100) if open_24h else 0
            
            # Доп. фильтрация на Python (если сложно в SQL)
            if strategy == 'volatility' and abs(change_pct) < 5:
                continue
            
            # Генерация URL логотипа
            if row['cmc_id']:
                image_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{row['cmc_id']}.png"
            else:
                image_url = f"https://assets.coincap.io/assets/icons/{row['symbol'].split('/')[0].lower()}@2x.png"

            result.append({
                "id": row['symbol'].replace('/', '').lower(),
                "symbol": row['symbol'].split('/')[0],
                "name": row['symbol'].split('/')[0],
                "image": image_url,
                "current_price": price,
                "price_change_percentage_24h": round(change_pct, 2),
                "market_cap": row['market_cap'] or 0,
                "total_volume": row['volume_24h'] or 0,
                "rsi": round(row['rsi_14'], 2) if row['rsi_14'] is not None else 50.0, 
                "macd": round(row['macd'], 2) if row['macd'] is not None else 0,
                "sparkline_in_7d": {
                    "price": row['sparkline'] or []
                }
            })
            
        return result

    except Exception as e:
        print(f"Error fetching coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))
