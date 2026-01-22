# 🚀 Crypto Screener (TWA)

A professional-grade real-time cryptocurrency screener built for Telegram Web Apps.

## 🌟 Key Features

### ⚡ Real-Time & Performance
- **Live Data:** <1s latency updates from Binance Spot via WebSocket.
- **Instant UX:** Smart Prefetching, Progressive Loading (200->3000 candles), and Gzip compression.
- **Haptic Feedback:** "Ratchet" scroll effect and tactile interactions.

### 📊 Advanced Analytics
- **Interactive Charts:** TradingView-style charts with 9 timeframes (1m - 1w).
- **Dynamic Indicators:** Client-side calculation of RSI, MACD, EMA, Bollinger Bands for any timeframe.
- **Signal Strength:** Composite "Buy/Sell" gauge aggregating multiple technical indicators.
- **Sparklines:** 24h trend visualization directly in the coin list.

### 💎 Data Richness
- **Market Cap:** Accurate data synced from CoinMarketCap (Top 3000 coverage).
- **Logos:** High-quality icons.
- **Deep History:** Access to months of 1m candle data stored in TimescaleDB.

## 🛠 Tech Stack
- **Frontend:** Next.js 14, Chakra UI, Zustand, TanStack Query v5, Lightweight Charts.
- **Backend:** Python 3.10, FastAPI, CCXT (Async), TimescaleDB, AIOHTTP.
- **Infrastructure:** Docker Compose, DigitalOcean Droplet (8 vCPU / 16GB RAM).

## 🚀 Quick Start (Local Dev)

### Frontend
```bash
npm install
npm run dev
# Open http://localhost:3000
```

### Backend
*Requires Docker*
```bash
cd backend
docker compose up -d --build
# API: http://localhost:8000
```

## 📦 Deployment

### Frontend (Vercel)
Push to `main` branch triggers auto-deployment.

### Backend (DigitalOcean)
SSH into server and run:
```bash
cd ~/cryptoscreener/backend
git pull
# Ensure .env has POSTGRES credentials and CMC_API_KEY
sudo docker compose up -d --build
```

## 📚 Documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System Overview
- [BACKEND_STATUS.md](./BACKEND_STATUS.md) - Infrastructure, Services & API
- [FRONTEND_STATUS.md](./FRONTEND_STATUS.md) - UI Components & Optimizations