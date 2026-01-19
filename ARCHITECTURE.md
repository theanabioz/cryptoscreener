# 🏗 System Architecture: Crypto Screener

## Overview
A real-time cryptocurrency screener and analytics platform deployed on DigitalOcean (Backend) and Vercel (Frontend).
The system is designed for High-Frequency updates (1s latency) and Deep Historical Analysis (2 years of 1m candles).

## 🧩 Components

### 1. Frontend (Next.js 14)
- **Host:** Vercel (HTTPS)
- **Tech Stack:** React, TypeScript, Chakra UI v2, Zustand, TanStack Query.
- **Key Features:**
  - **Proxy Route (`/api/coins`):** Routes requests to DigitalOcean to avoid Mixed Content / CORS issues.
  - **Live UI:** Updates prices every second via polling (soon to be WebSocket).
  - **Charting:** TradingView Lightweight Charts with interactive history.
  - **TWA:** Fully integrated Telegram Web App (BackButton, Haptics, User Data).

### 2. Backend (FastAPI + Data Collector)
- **Host:** DigitalOcean Droplet (Ubuntu, Docker)
- **Tech Stack:** Python 3.10, FastAPI, Pandas, CCXT, PyArrow.
- **Services:**
  - **Collector:** Autonomous background worker that harvests 2 years of 1m OHLCV data from Binance into Parquet files.
  - **Market Data Manager:** In-memory state manager connected to Binance WebSocket (`!miniTicker@arr`).
  - **TA Worker:** Background process calculating RSI, MACD, EMA on 1h timeframe for all active coins.

### 3. Data Flow
1. **Historical Data:** `Binance REST -> Collector -> Parquet Files -> (Future: TimescaleDB)`
2. **Real-time Price:** `Binance WS -> MarketDataManager (RAM) -> API Endpoint -> Frontend`
3. **Indicators:** `Binance REST (1h candles) -> TA Worker -> MarketDataManager (RAM)`

## 🔄 Current Status
- **Phase:** Data Harvesting & MVP Stabilization.
- **Goal:** Migration to TimescaleDB for instant historical access and complex queries.

## 🛠 Deployment
- **Frontend:** `git push` -> Vercel Auto-deploy.
- **Backend:**
  ```bash
  cd backend
  git pull
  sudo docker compose up -d --build
  ```
