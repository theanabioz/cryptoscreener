import { Coin } from './types';

export const MOCK_COINS: Coin[] = [
  {
    id: 'bitcoin',
    symbol: 'BTC',
    name: 'Bitcoin',
    image: 'https://s2.coinmarketcap.com/static/img/coins/64x64/1.png',
    current_price: 65432.10,
    price_change_percentage_24h: 2.5,
    market_cap: 1200000000000,
    total_volume: 35000000000,
    sparkline_in_7d: { price: [64000, 64500, 65000, 64800, 65200, 65432] }
  },
  {
    id: 'ethereum',
    symbol: 'ETH',
    name: 'Ethereum',
    image: 'https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png',
    current_price: 3456.78,
    price_change_percentage_24h: -1.2,
    market_cap: 400000000000,
    total_volume: 15000000000,
    sparkline_in_7d: { price: [3550, 3500, 3480, 3460, 3440, 3456] }
  }
];