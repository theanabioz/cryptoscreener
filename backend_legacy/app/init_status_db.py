import asyncio
from database import db

async def init_db():
    print("Initializing database tables...")
    
    # 1. Таблица статусов (RSI, Цена и т.д.)
    query_status = """
    CREATE TABLE IF NOT EXISTS coin_status (
        symbol TEXT PRIMARY KEY,
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        current_price DOUBLE PRECISION,
        price_change_24h DOUBLE PRECISION,
        volume_24h DOUBLE PRECISION,
        market_cap DOUBLE PRECISION,
        rsi_14 DOUBLE PRECISION,
        macd DOUBLE PRECISION,
        macd_signal DOUBLE PRECISION,
        macd_hist DOUBLE PRECISION,
        ema_50 DOUBLE PRECISION,
        bb_upper DOUBLE PRECISION,
        bb_lower DOUBLE PRECISION
    );
    """
    
    # 2. Таблица метаданных (Список монет) - Правильный справочник
    query_meta = """
    CREATE TABLE IF NOT EXISTS coins_meta (
        symbol TEXT PRIMARY KEY,
        is_active BOOLEAN DEFAULT TRUE,
        added_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    try:
        await db.pool.execute(query_status)
        await db.pool.execute(query_meta)
        
        # 3. Начальное наполнение coins_meta (если пусто)
        # Мы делаем это один раз тяжелым запросом, чтобы потом работать быстро
        # Используем INSERT ON CONFLICT DO NOTHING
        print("Populating coins_meta from candles (this might take a while once)...")
        populate_query = """
        INSERT INTO coins_meta (symbol)
        SELECT DISTINCT symbol FROM candles
        ON CONFLICT DO NOTHING;
        """
        await db.pool.execute(populate_query)
        
        print("✅ Tables initialized successfully.")
        
    except Exception as e:
        print(f"❌ Error initializing tables: {e}")

if __name__ == "__main__":
    async def main():
        await db.connect()
        await init_db()
        await db.close()
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())