# 🚀 Crypto Screener (TWA)

Professional-grade real-time cryptocurrency screener for Telegram Web Apps.

## ⚡ Current Capabilities
- **Performance:** Instant chart switching, lazy prefetching, and Gzip compression.
- **Analytics:** Dynamic indicators (RSI, MACD, EMA, BB) calculated instantly on the client.
- **Trust:** Data synced from Binance Spot and CoinMarketCap.
- **Infrastructure:** Hardened 8-core server with optimized TimescaleDB storage.

## 🛠 Tech Stack
- **Frontend:** Next.js 14, Chakra UI, Zustand, TanStack Query, Lightweight Charts.
- **Backend:** Python 3.10, FastAPI, CCXT, TimescaleDB, Redis (Planned).
- **Security:** Private DB network, resource isolation.

## 🎯 Next Objective: WebSocket Transition
We are moving from HTTP Polling to a full WebSocket + Redis architecture to provide true "tick-by-tick" data updates while further reducing server load.

## 📚 Detailed Status
- [BACKEND_STATUS.md](./BACKEND_STATUS.md)
- [FRONTEND_STATUS.md](./FRONTEND_STATUS.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
