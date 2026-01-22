# 🚀 Crypto Screener (TWA)

A professional-grade real-time cryptocurrency screener built for Telegram.

## 🌟 Key Features
- **Real-time Data:** <1s latency updates from Binance Spot (450+ pairs).
- **Interactive Charts:** TradingView-style charts with 9 timeframes (1m - 1w).
- **Sparklines:** 24h trend visualization directly in the coin list.
- **Technical Analysis:** RSI, MACD, EMA, Bollinger Bands calculated server-side.
- **Deep History:** Access to months of 1m candle data stored in TimescaleDB.
- **Mobile First:** Optimized for Telegram Web App (iOS/Android).

## 🛠 Tech Stack
- **Frontend:** Next.js 14, Chakra UI, Zustand, Lightweight Charts.
- **Backend:** Python 3.10, FastAPI, CCXT (Async), TimescaleDB.
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
sudo docker compose up -d --build
```

## 📚 Documentation
For detailed architectural decisions and status, see:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System Overview
- [BACKEND_STATUS.md](./BACKEND_STATUS.md) - Infrastructure & Services
- [FRONTEND_STATUS.md](./FRONTEND_STATUS.md) - UI/UX & Features
