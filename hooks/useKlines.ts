import { useQuery } from '@tanstack/react-query';

export interface Kline {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

const fetchKlines = async (symbol: string, interval: string): Promise<Kline[]> => {
  // Ensure we request the full pair (e.g., BTC -> BTCUSDT)
  const pair = symbol.toUpperCase().includes('USDT') ? symbol : `${symbol}USDT`;
  const res = await fetch(`/api/klines/${pair}?interval=${interval}&limit=500`);
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  return res.json();
};

export const useKlines = (symbol: string, interval: string) => {
  return useQuery({
    queryKey: ['klines', symbol, interval],
    queryFn: () => fetchKlines(symbol, interval),
    staleTime: 1000 * 60, // 1 minute
    enabled: !!symbol, // Only fetch if symbol exists
  });
};
