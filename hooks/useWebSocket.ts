import { useEffect, useRef } from 'react';
import { usePriceStore } from '@/store/usePriceStore';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export const useWebSocket = () => {
  const ws = useRef<WebSocket | null>(null);
  const updatePrice = usePriceStore((state) => state.updatePrice);

  useEffect(() => {
    let isMounted = true;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      if (!isMounted) return;
      if (ws.current?.readyState === WebSocket.OPEN) return;

      // Close existing if any (avoid dupes)
      if (ws.current) {
        ws.current.close();
      }

      console.log('🔌 Connecting to WS:', WS_URL);
      const socket = new WebSocket(WS_URL);
      ws.current = socket;

      socket.onopen = () => {
        console.log('✅ WS Connected to:', WS_URL);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Expected format: { s: "BTC/USDT", k: [t, o, h, l, c, v] }
          if (data.s && data.k) {
            // Strip /USDT to match frontend symbol (e.g. "BTC/USDT" -> "BTC")
            const cleanSymbol = data.s.split('/')[0];
            updatePrice(cleanSymbol, data.k);
          }
        } catch (e) {
          console.error('WS Parse Error', e);
        }
      };

      socket.onclose = () => {
        if (isMounted) {
            console.log('⚠️ WS Closed. Reconnecting in 3s...');
            reconnectTimeout = setTimeout(connect, 3000);
        }
      };

      socket.onerror = (err) => {
         console.error('WS Error:', err);
         socket.close(); // Ensure close is triggered to start reconnection
      };
    };

    connect();

    return () => {
      isMounted = false;
      clearTimeout(reconnectTimeout);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [updatePrice]);
};
