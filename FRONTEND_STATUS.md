# ⚛️ Frontend Technical Status

## Architecture
- **Framework:** Next.js 14 (App Router) + TypeScript.
- **Styling:** Chakra UI v2 (Dark Theme `#171923`).
- **State Management:** Zustand (`useFilterStore`, `useWatchlistStore`).
- **Data Fetching:** TanStack Query v5 (`useCoins`, `useKlines`) with advanced caching.

## 🌟 Key Features

### Screener (Home)
- **Instant Navigation:** Prefetching for top-15 coins + Lazy Prefetching on scroll (IntersectionObserver).
- **Sparklines:** Real-time SVG charts in the list showing 24h trend (Red/Green dynamic coloring).
- **Haptics:** "Ratchet" style haptic feedback when scrolling list (`useScrollHaptic`).
- **Data:** Sorted by Market Cap, real-time price updates (1s polling).

### Coin Detail Page
- **Chart:** `lightweight-charts` with 9 timeframes.
- **Performance:** 
  - **Progressive Loading:** Loads 200 candles instantly -> loads 3000 in background.
  - **Zero Flicker:** Uses `placeholderData` for seamless history updates.
  - **Optimized Rendering:** Chart instance is reused, only data is updated via `setData`.
- **Dynamic Analysis:**
  - **Client-side TA:** RSI, MACD, EMA, Bollinger calculate instantly upon timeframe change (`lib/indicators.ts`).
  - **Signal Strength:** Composite Gauge indicating Buy/Sell sentiment based on 4 indicators.

### UX & Polish
- **Telegram Integration:** Native colors (Header/BG) matches app theme, Back Button integration.
- **iOS Optimization:** Fixed "white overscroll" issue via `theme-color` and CSS overrides.
- **Navigation:** Preserves scroll position and cache (gcTime 1h) for instant "Back" navigation.

## 🔌 API Integration
- **Proxy:** Next.js API Routes act as secure proxy to Python Backend.
- **Optimization:** Backend responses are Gzip-compressed.

## 📝 TODO / Next Steps
1. **[COMPLETED] Performance:** Full prefetching and progressive loading implemented.
2. **[COMPLETED] Visuals:** Sparklines, CMC Logos, Signal Gauge.
3. **Alerts UI:** Interface for setting price alerts.
4. **Portfolio:** User portfolio tracking.