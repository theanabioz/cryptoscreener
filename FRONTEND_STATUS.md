# ⚛️ Frontend Technical Status

## 🌟 Key Features
- **Fast Navigation:** Progressive loading (200 -> 3000 candles) and intelligent prefetching using Intersection Observer.
- **Dynamic Indicators:** Client-side calculation of RSI (Wilder's), MACD, EMA, and Bollinger Bands for any timeframe.
- **Visual Polish:** Sparklines, Signal Strength Gauge, Haptic feedback ("ratchet" scroll).
- **Mobile First:** Optimized for Telegram iOS/Android (Overscroll fixes, native color matching).

## 🔌 API Integration
- **Current:** HTTP Polling every 1000ms via TanStack Query.
- **Target:** Persistent WebSocket connection for instant updates.

## 📱 Performance Fixes
- **Chart Re-use:** Optimized `DetailChart` to prevent re-creating chart instances on every data update.
- **Gzip Support:** Frontend handles compressed payloads for faster data transfer.

## 📝 TODO / Next Steps
1. **[IN PROGRESS] WebSocket Migration:** Replace polling with real-time push.
2. **Advanced Charting:** Add drawing tools and technical overlays.
3. **User Auth:** Telegram-based authentication for personalized watchlists and alerts.
