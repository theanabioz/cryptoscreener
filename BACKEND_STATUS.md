# 🐍 Backend Technical Status

## Current Infrastructure
- **Server:** 8 vCPU, 16GB RAM, 150GB NVMe (Production).
- **Docker Compose V2:** Orchestrates `api`, `streamer`, `worker`, `timescaledb`.
- **Service `timescaledb`:** **RUNNING** (Storing historical & realtime data).
- **Service `streamer`:** **RUNNING** (Real-time WebSocket data ingestion).
- **Service `api`:** **RUNNING** (FastAPI serving data to Frontend with Gzip).

## 📂 Data & Database
- **Database:** TimescaleDB (PostgreSQL 14).
- **Table `candles`:** Hypertable with compression. Columns: `time, symbol, open, high, low, close, volume`.
- **Table `coin_status`:** Stores latest indicators and metadata (Market Cap, CMC ID).
- **Retention:** 2 years.
- **Real-time:** `streamer` inserts/upserts data every <1s using batch processing.

## 🧠 Services Codebase

### `app/streamer.py` (Realtime)
- **Architecture:** Producer-Consumer pattern with `asyncio.Queue`.
- **Features:** 450+ individual WebSocket tasks, optimized batch DB writing (30 items/batch).
- **Resilience:** Auto-reconnect, error handling for `aiohttp` compatibility.

### `app/worker.py` (Technical Analysis)
- **Role:** Calculates indicators (RSI, MACD, EMA, Bollinger) for the screener.
- **Frequency:** Runs every minute for all active coins.
- **Output:** Updates `coin_status` table for fast retrieval by the API.

### `app/sync_cmc.py` (Metadata Sync)
- **Role:** Fetches Market Cap and Coin IDs from CoinMarketCap API.
- **Strategy:** Uses `/quotes/latest` endpoint with chunking (20 symbols/request) to handle 450+ pairs efficiently.
- **Features:**
  - Robust mapping (e.g., `1000SATS` -> `SATS`, `BTTC` -> `BTT`).
  - Filtering of non-ASCII symbols.
  - Updates `market_cap` and `cmc_id` in DB.

### `app/routers/klines.py`
- **Timeframes:** `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`.
- **Aggregation:** Uses TimescaleDB `time_bucket` for on-the-fly aggregation.
- **Performance:** Optimized SQL queries.

### `app/routers/screener.py`
- **Features:** Returns rich coin data including `sparkline` arrays (24h), `market_cap`, `macd_signal`, `bb_upper/lower`.
- **Logos:** Generates high-quality CoinMarketCap logo URLs based on `cmc_id`.
- **Sorting:** Default sort by Market Cap (DESC).

## 🚀 Roadmap
1. **[COMPLETED] Real-time Engine:** WebSocket Streamer + TimescaleDB.
2. **[COMPLETED] Metadata:** CMC Integration for Market Cap & Logos.
3. **[COMPLETED] API Performance:** Gzip middleware, optimized queries.
4. **[NEXT] Advanced Strategies:** Implement complex filtering logic (Pump Radar).
5. **[NEXT] Alerts:** Push notification service.

## ⚠️ Notes
- **API Keys:** `CMC_API_KEY` is managed via `.env` on the server.
- **Optimization:** `streamer` is tuned for high throughput.