# ⚛️ Frontend Technical Status

## Architecture
- **Framework:** Next.js 14 (App Router).
- **Styling:** Chakra UI v2 (Dark Mode default).
- **State:** Zustand (`useFilterStore`, `useWatchlistStore`).
- **Data:** TanStack Query (`useCoins`, `useKlines`).

## 🔌 API Integration
### Proxy Pattern
To avoid Mixed Content (HTTPS -> HTTP) and CORS:
- **Client:** Fetches `/api/coins` (Next.js Route Handler).
- **Next.js Server:** Fetches `http://142.93.171.76:8000/api/coins` (DigitalOcean).
- **Headers:** `Cache-Control: no-store` is enforced to prevent Vercel from caching real-time data.

### Live Updates
- **Global:** `useCoins` polls every **1000ms** (1s).
- **Visuals:** `PriceFlash` component animates color changes (Green/Red) on price update.

## 📱 Mobile / Telegram UX
- **Navigation:** Bottom Tab Bar + Native Telegram Back Button.
- **Filters:** Full Screen Page (`/filters`) to avoid iOS keyboard layout shifts.
- **Header:** Sticky, safe-area aware (`viewport-fit=cover`), centrally aligned titles to avoid overlapping with Telegram controls.

## 📊 Charting
- **Lib:** `lightweight-charts` (TradingView).
- **Data Source:** `/api/klines/[symbol]` (Proxy to Backend).
- **Live Candle:** `DetailChart.tsx` merges historical Klines with the current live price from WebSocket to animate the last candle in real-time.

## 📝 TODO / Next Steps
- **WebSockets:** Move from Polling (1s fetch) to a real WebSocket connection for the Frontend for smoother "tick-by-tick" updates.
- **Virtualization:** If the list grows > 500 items, implement `react-window` to save DOM nodes.
