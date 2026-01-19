export interface Coin {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_percentage_24h: number;
  market_cap: number;
  total_volume: number;
  sparkline_in_7d?: {
    price: number[];
  };
  image: string;
}

export type MarketCapFilter = 'all' | 'high' | 'mid' | 'low'; // >1B, 100M-1B, <100M
export type PriceChangeFilter = 'all' | 'gainers' | 'losers';

export interface ScreenerFilter {
  search: string;
  minPrice: string; // string allows empty input
  maxPrice: string;
  marketCap: MarketCapFilter;
  priceChange: PriceChangeFilter;
}