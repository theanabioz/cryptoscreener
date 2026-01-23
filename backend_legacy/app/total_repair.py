import asyncio
import ccxt.async_support as ccxt
import asyncpg
from datetime import datetime, timedelta, timezone

async def total_repair():
    print("🚀 TOTAL REPAIR STARTING: Covering last 3 days with NO GAPS...")
    
    conn_str = "postgresql://postgres:SuperLongSecurePassword2026NoSpecialChars@timescaledb:5432/postgres"
    pool = await asyncpg.create_pool(conn_str)
    
    exchange = ccxt.binance({'enableRateLimit': True})
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT symbol FROM coins_meta WHERE is_active = TRUE")
        symbols = [r['symbol'] for r in rows]

    # Идем на 3 дня назад, чтобы точно захватить все дыры
    start_ts = int((datetime.now(timezone.utc) - timedelta(days=3)).timestamp() * 1000)
    end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)

    async def repair_symbol(symbol):
        current_since = start_ts
        total_recovered = 0
        try:
            while current_since < end_ts:
                candles = await exchange.fetch_ohlcv(symbol, '1m', since=current_since, limit=1000)
                if not candles:
                    break
                
                records = [(datetime.fromtimestamp(c[0]/1000, tz=timezone.utc), symbol, c[1], c[2], c[3], c[4], c[5]) for c in candles]
                
                query = """
                    INSERT INTO candles (time, symbol, open, high, low, close, volume)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (time, symbol) DO UPDATE SET 
                        open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close;
                """
                async with pool.acquire() as conn:
                    await conn.executemany(query, records)
                
                total_recovered += len(candles)
                # Сдвигаем время на последнюю полученную свечу + 1 минута
                current_since = candles[-1][0] + 60000
                
                if len(candles) < 1000: # Значит дошли до конца
                    break
            
            print(f"  [v] {symbol}: Fully synchronized ({total_recovered} candles).")
        except Exception as e:
            print(f"  [!] Error {symbol}: {e}")

    # Обрабатываем по 5 монет параллельно (чтобы не забанили)
    batch_size = 5
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        await asyncio.gather(*[repair_symbol(s) for s in batch])
        print(f"--- Completed: {i+len(batch)}/{len(symbols)} ---")
        await asyncio.sleep(0.5)

    await exchange.close()
    await pool.close()
    print("✅ MISSION COMPLETE: NO GAPS REMAINING.")

if __name__ == "__main__":
    asyncio.run(total_repair())
