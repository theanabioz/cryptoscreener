from fastapi import APIRouter, HTTPException, Query
from database import db
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
        "3m": "3 minutes",
        "5m": "5 minutes",
        "15m": "15 minutes",
        "30m": "30 minutes",
        "1h": "1 hour",
        "4h": "4 hours",
        "1d": "1 day",
        "1w": "1 week",
    }
    
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail="Invalid interval")
    
    bucket = valid_intervals[interval]

    # SQL запрос с агрегацией (Time Bucket)
    # TimescaleDB умеет сам собирать 1m свечи в 5m, 1h и т.д.
    query = f"""
        SELECT 
            time_bucket('{bucket}', time) AS bucket_time,
            FIRST(open, time) as open,
            MAX(high) as high,
            MIN(low) as low,
            LAST(close, time) as close,
            SUM(volume) as volume
        FROM candles
        WHERE symbol = $1
        GROUP BY bucket_time
        ORDER BY bucket_time DESC
        LIMIT $2
    """

    try:
        rows = await db.fetch_all(query, symbol, limit)
        
        if not rows:
            return []

        result = [
            {
                "time": int(row["bucket_time"].timestamp()),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"]
            }
            for row in reversed(rows)
        ]
        
        return result

    except Exception as e:
        print(f"Error fetching klines: {e}")
        raise HTTPException(status_code=500, detail=str(e))
