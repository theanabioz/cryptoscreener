import { create } from 'zustand'

export interface CandleData {
  t: number; // time
  o: number; // open
  h: number; // high
  l: number; // low
  c: number; // close
  v: number; // volume
}

interface PriceState {
  prices: Record<string, CandleData>;
  updatePrice: (symbol: string, candle: number[]) => void;
  bulkUpdate: (updates: Record<string, number[]>) => void;
  getPrice: (symbol: string) => CandleData | undefined;
}

export const usePriceStore = create<PriceState>((set, get) => ({
  prices: {},
  updatePrice: (symbol, c) => set((state) => ({
    prices: {
      ...state.prices,
      [symbol]: { t: c[0], o: c[1], h: c[2], l: c[3], c: c[4], v: c[5] }
    }
  })),
  bulkUpdate: (updates) => set((state) => {
    const newPrices = { ...state.prices };
    Object.entries(updates).forEach(([symbol, c]) => {
      newPrices[symbol] = { t: c[0], o: c[1], h: c[2], l: c[3], c: c[4], v: c[5] };
    });
    return { prices: newPrices };
  }),
  getPrice: (symbol) => get().prices[symbol],
}))
