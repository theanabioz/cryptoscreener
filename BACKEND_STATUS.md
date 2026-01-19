# 🐍 Backend Technical Status

## Current Infrastructure
- **Docker Compose V2:** Orchestrates services.
- **Service `collector`:** Currently running a massive download job (646 pairs, 2 years history).
- **Service `api`:** NOT RUNNING (Stopped to allow Collector to finish). *Note: Once collector finishes, we will bring API back or migrate to DB.*

## 📂 Data Structure
- **Path:** `backend/data/raw_parquet/`
- **Format:** Parquet (Snappy compression).
- **Naming:** `BTCUSDT.parquet`
- **Schema:** `time (datetime), open, high, low, close, volume`

## 🧠 Services Codebase
### `collector/download.py`
- Uses `ccxt` with `enableRateLimit=True`.
- Fetches all `*USDT` pairs from Binance Spot.
- Chunks download into 1000-candle requests.
- Skips already existing files (Resume capability).

### `app/services/market_data.py` (Archived in API)
- Connects to `wss://stream.binance.com:9443/ws/!miniTicker@arr`.
- Maintains a Python `Dict` with latest prices.
- Supports `dict.update()` to merge TA indicators with live prices.

### `app/services/technical_analysis.py` (Archived in API)
- Fetches 1h candles for active symbols.
- Calculates RSI (14), EMA (50), MACD, Bollinger Bands using `ta` library.
- Updates `market_manager` state.

## 🚀 Roadmap to V2.0 (Database Era)
1. **Finish Download:** Wait for Collector to finish (est. 18 hours).
2. **Deploy TimescaleDB:** Add `timescaledb` service to docker-compose.
3. **Ingest:** Write a script to load Parquet files into TimescaleDB using `pgcopy` (Bulk Insert).
4. **Rewrite API:**
   - Stop storing state in RAM (except simple caching).
   - Read Historical Klines from DB (Instant response).
   - Read Live Price from Redis or keep WebSocket memory.

## ⚠️ Known Issues / Notes
- **Memory:** Storing 450 coins with full history in RAM is impossible. That's why we moved to Parquet/DB approach.
- **Rate Limits:** Collector respects Binance limits, but multiple restarts might trigger temporary IP bans.
