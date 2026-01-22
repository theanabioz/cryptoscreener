# ⚛️ Frontend Technical Status

## Architecture
- **Framework:** Next.js 14 (App Router).
- **Styling:** Chakra UI v2 (Dark Mode default).
- **State:** Zustand (`useFilterStore`, `useWatchlistStore`).
- **Data:** TanStack Query (`useCoins`, `useKlines`) with optimized polling.

## 🔌 API Integration
### Backend Connection
- **Status:** Connected to production API.
- **Proxy:** Next.js API Routes (`/api/coins`, `/api/klines/*`) act as secure proxy to Python Backend.

### Live Updates
- **Screener:** `useCoins` polls every **1000ms** (1s).
- **Charts:** `useKlines` fetches updated candles.
- **Sparklines:** Real-time visualization of 24h trend in coin list.
- **Visuals:** `PriceFlash` component for tick-by-tick animation.

## 📱 Mobile / Telegram UX
- **Coin List:** `AccordionCoinItem` with integrated Sparkline and details.
- **Navigation:** Bottom Tab Bar + Native Telegram Back Button.
- **Filters:** Full Screen Page (`/filters`).

## 📊 Charting
- **Lib:** `lightweight-charts` (TradingView).
- **Features:**
  - **Timeframes:** 1M, 3M, 5M, 15M, 30M, 1H, 4H, 1D, 1W.
  - **History:** Deep history support (3000 candles).
  - **Sparklines:** Minimalist SVG charts in lists (Red/Green based on trend).

## 📝 TODO / Next Steps
1. **[COMPLETED] Screener UI:** Accordion view with Sparklines.
2. **[COMPLETED] Deep Charts:** Added more timeframes and history depth.
3. **Alerts UI:** Interface for setting price alerts.
4. **Portfolio:** Simple portfolio tracking.
