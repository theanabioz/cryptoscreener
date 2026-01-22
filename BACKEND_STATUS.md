# 🐍 Backend Technical Status

## Current Infrastructure
- **Server:** 8 vCPU, 16GB RAM, 150GB NVMe.
- **Docker Compose V2:** Orchestrates `api`, `streamer`, `worker`, `timescaledb`.
- **Service `timescaledb`:** **RUNNING** (Storing historical & realtime data).
- **Service `streamer`:** **RUNNING** (Real-time WebSocket data ingestion).
- **Service `api`:** **RUNNING** (FastAPI serving data to Frontend).

## 📂 Data & Database
- **Database:** TimescaleDB (PostgreSQL 14).
- **Table:** `candles` (Hypertable with compression).
- **Columns:** `time, symbol, open, high, low, close, volume`.
- **Retention:** 2 years (configured policy).
- **Real-time:** `streamer` inserts/upserts data every <1s.

## 🧠 Services Codebase

### `app/streamer.py` (Refactored)
- **Architecture:** Producer-Consumer pattern with `asyncio.Queue`.
- **Producers:** 450+ individual tasks listening to Binance WebSocket (`watch_ohlcv`).
- **Consumer:** Batched DB Writer (writes 30-50 updates per batch) for high throughput.
- **Resilience:** Auto-reconnect, exponential backoff, individual symbol isolation.

### `app/routers/klines.py`
- **Timeframes:** Supports `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`.
- **Aggregation:** Uses TimescaleDB `time_bucket` for efficient on-the-fly aggregation.
- **History:** Supports retrieving deep history (limit up to 5000 candles).

### `app/routers/screener.py`
- **Sparklines:** Generates 24h hourly price arrays using SQL aggregation (`array_agg` + `time_bucket`).
- **Performance:** Optimized query for "Market" list view.

## 🚀 Roadmap
1. **[COMPLETED] Hardware Upgrade.**
2. **[COMPLETED] Data Harvesting & Ingestion.**
3. **[COMPLETED] Real-time Streamer:** Multi-task architecture, <1s latency.
4. **[COMPLETED] API V2:** Full support for charts, screener, and sparklines.
5. **[NEXT] Advanced Strategies:** Implement `pump-radar` and `volatility` logic in `worker.py`.
6. **[NEXT] Alerts:** Push notifications for price levels.

## ⚠️ Notes
- **Optimization:** `streamer` is tuned for stability (pinned `aiohttp < 3.10` due to CCXT compatibility).
- **Scalability:** System handles 450+ pairs effortlessly.
