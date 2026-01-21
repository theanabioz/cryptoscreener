from fastapi import APIRouter, HTTPException, Query
from app.database import db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query("1m", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(1000, le=5000, description="Max candles to return")
):
    """
    Получает исторические свечи из TimescaleDB.
    Автоматически агрегирует 1m свечи в более крупные таймфреймы (bucket).
    """
    
    # Приводим символ к формату базы (BTCUSDT -> BTC/USDT)
    # Если фронтенд шлет 'BTCUSDT', добавляем слэш
    if '/' not in symbol:
        symbol = symbol.replace('USDT', '/USDT')

    # Валидация интервалов для time_bucket
    valid_intervals = {
        "1m": "1 minute",
        "5m": "5 minutes",
        "15m": "15 minutes",
        "1h": "1 hour",
        "4h": "4 hours",
        "1d": "1 day",
    }
    
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail="Invalid interval")
    
    bucket = valid_intervals[interval]

    # SQL запрос с агрегацией (Time Bucket)
    # TimescaleDB умеет сам собирать 1m свечи в 5m, 1h и т.д.
    query = f"""
        SELECT 
            time_bucket('{bucket}', time) AS time,
            FIRST(open, time) as open,
            MAX(high) as high,
            MIN(low) as low,
            LAST(close, time) as close,
            SUM(volume) as volume
        FROM candles
        WHERE symbol = $1
        GROUP BY time
        ORDER BY time DESC
        LIMIT $2
    """

    try:
        rows = await db.fetch_all(query, symbol, limit)
        
        if not rows:
            # Попробуем без слэша, вдруг в базе по-другому
            # (Хотя мы вроде договорились писать со слэшем)
            return []

        # Форматируем ответ для Lightweight Charts (time: timestamp, value: float)
        # Lightweight Charts ждет время в секундах (unix timestamp)
        # Сортируем по возрастанию (ASC) для графика
        result = [
            {
                "time": int(row["time"].timestamp()),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"]
            }
            for row in reversed(rows) # Разворачиваем, так как из БД брали DESC (последние)
        ]
        
        return result

    except Exception as e:
        print(f"Error fetching klines: {e}")
        raise HTTPException(status_code=500, detail=str(e))
