# ⚛️ Frontend Technical Status

## Architecture
- **Framework:** Next.js 14 (App Router).
- **Styling:** Chakra UI v2 (Dark Mode default).
- **State:** Zustand (`useFilterStore`, `useWatchlistStore`).
- **Data:** TanStack Query (`useCoins`, `useKlines`).

## 🔌 API Integration
### Backend Connection
- **Config:** Migrated from hardcoded IP to `BACKEND_URL` environment variable.
- **Current State:** Ready to connect to the new powerful server.

### Live Updates
- **Global:** `useCoins` polls every **1000ms** (1s).
- **Visuals:** `PriceFlash` component animates color changes (Green/Red).

## 📱 Mobile / Telegram UX
- **Navigation:** Bottom Tab Bar + Native Telegram Back Button.
- **Layout:** Optimized "Accordion" style list planned for Screener to avoid horizontal scrolling.
- **Filters:** Full Screen Page (`/filters`).

## 📊 Charting
- **Lib:** `lightweight-charts` (TradingView).
- **Data Source:** Currently proxying to Backend. Next step: fetch directly from new DB API.

## 📝 TODO / Next Steps
1. **Connect to New API:** Update `.env` with new server IP.
2. **Screener UI:** Implement "Accordion" view for mobile-friendly data display.
3. **WebSockets:** Move from Polling to WS for real-time feed.