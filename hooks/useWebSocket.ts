import { useEffect, useRef } from 'react';
import { usePriceStore } from '@/store/usePriceStore';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export const useWebSocket = () => {
  const ws = useRef<WebSocket | null>(null);
  const bulkUpdate = usePriceStore((state) => state.bulkUpdate);
  const buffer = useRef<Record<string, number[]>>({});

  useEffect(() => {
    let isMounted = true;
    let reconnectTimeout: NodeJS.Timeout;
    let flushInterval: NodeJS.Timeout;

    const connect = () => {
      if (!isMounted) return;
      if (ws.current?.readyState === WebSocket.OPEN) return;

      if (ws.current) ws.current.close();

      console.log('🔌 Connecting to WS:', WS_URL);
      const socket = new WebSocket(WS_URL);
      ws.current = socket;

      socket.onopen = () => {
        console.log('✅ WS Connected to:', WS_URL);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.s && data.k) {
            const cleanSymbol = data.s.split('/')[0];
            // Accumulate in buffer
            buffer.current[cleanSymbol] = data.k;
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

      socket.onerror = () => {
         socket.close();
      };
    };

    // Periodically flush buffer to store (2 times per second)
    flushInterval = setInterval(() => {
        if (Object.keys(buffer.current).length > 0) {
            bulkUpdate(buffer.current);
            buffer.current = {}; // Clear buffer
        }
    }, 500);

    connect();

    return () => {
      isMounted = false;
      clearTimeout(reconnectTimeout);
      clearInterval(flushInterval);
      if (ws.current) ws.current.close();
    };
  }, [bulkUpdate]);
};
