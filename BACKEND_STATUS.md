# 🐍 Backend Technical Status

## 🛡️ Security Status
- **Incident Response (2026-01-22):** Successfully detected and eliminated `kdevtmpfsi` miner malware.
- **Hardening:** 
  - Database port `5432` is now **CLOSED** to the public internet (internal Docker network only).
  - Credentials updated.
  - Periodic resource monitoring implemented.

## 🚀 Infrastructure & Performance
- **Server:** 8 vCPU, 16GB RAM. Current Load: ~20-30% CPU (Healthy).
- **Streamer Optimization:** Batched DB writes (1000 items / 1s delay) to prevent DB thrashing.
- **Screener Optimization:** Pre-calculated sparklines in `coin_status` table. API reads ready-to-use JSON instead of performing heavy SQL aggregations.
- **Gzip:** All API responses are compressed.

## 📂 Data Structure
- **Table `candles`:** Stores raw 1m data (real-time & history).
- **Table `coin_status`:** Stores latest prices, indicators, and pre-calculated sparklines for fast listing.

## 🧠 Services
- **`streamer.py`:** Collects data from Binance.
- **`worker.py`:** Calculates TA indicators and sparklines periodically.
- **`api/`:** FastAPI routes serving the frontend.

## 🚀 Roadmap
1. **[COMPLETED] Real-time Engine & History.**
2. **[COMPLETED] Production Hardening & Performance Fixes.**
3. **[COMPLETED] WebSocket + Redis Architecture:**
   - Implemented Redis Pub/Sub (`streamer.py` -> Redis).
   - Created WebSocket endpoint (`routers/ws.py` -> Client).
   - Replaced HTTP Polling with real-time push.
4. **[PLANNED] Alerts & Notifications.**
