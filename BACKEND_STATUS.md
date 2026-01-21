# 🐍 Backend Technical Status

## Current Infrastructure
- **Server:** 8 vCPU, 16GB RAM, 150GB NVMe (Ready for high load).
- **Docker Compose V2:** Orchestrates services.
- **Service `timescaledb`:** **RUNNING** (Storing historical data).
- **Service `collector`:**
  - **Status:** Finished downloading 90 days of history for 450 pairs.
  - **Task:** Currently ingesting Parquet files into TimescaleDB.

## 📂 Data Structure
- **Raw Storage:** `backend/data/raw_parquet/` (Local backup of 90 days history).
- **Database:** TimescaleDB (PostgreSQL 14).
  - **Table:** `candles` (Hypertable with compression).
  - **Columns:** `time, symbol, open, high, low, close, volume`.
  - **Retention:** 2 years (configured policy).
  - **Compression:** After 3 days (by symbol).

## 🧠 Services Codebase
### `collector/download.py`
- Optimized for 90 days history (`DAYS = 90`).
- Successfully downloaded ~1GB of data.

### `collector/ingest_parquet.py`
- **New Script:** Reads Parquet files and bulk inserts them into TimescaleDB using SQLAlchemy.
- **Features:** Progress bar (`tqdm`), automatic dependency installation.

## 🚀 Roadmap
1. **[COMPLETED] Hardware Upgrade:** Migrated to 8 vCPU / 16GB RAM server.
2. **[COMPLETED] Data Harvesting:** Downloaded 90 days of 1m candles.
3. **[IN PROGRESS] Database Ingestion:** Populating TimescaleDB.
4. **[NEXT] API V2:**
   - Connect FastAPI to TimescaleDB.
   - Serve historical klines from DB instead of FileSystem/Binance Proxy.
   - Implement real-time WebSocket updates.

## ⚠️ Notes
- **Backups:** Raw Parquet files are stored locally as a safety net.
- **Performance:** Ingestion speed is ~6-9 sec/coin due to index building. Total time est. ~1 hour.