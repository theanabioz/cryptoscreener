import asyncio
import json
import logging
import websockets
from typing import Dict, List
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketDataManager, cls).__new__(cls)
            cls._instance.prices: Dict[str, dict] = {}
            cls._instance.running = False
        return cls._instance

    async def start_stream(self):
        """Запускает WebSocket соединение с Binance"""
        self.running = True
        url = f"{settings.BINANCE_WS_URL}/!miniTicker@arr"
        
        logger.info(f"Connecting to Binance Stream: {url}")
        
        while self.running:
            try:
                async with websockets.connect(url) as ws:
                    logger.info("Connected to Binance WebSocket!")
                    
                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        self._process_message(data)
            except Exception as e:
                logger.error(f"WebSocket Error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    def _process_message(self, data: List[dict]):
        """
        Обрабатывает поток !miniTicker@arr.
        Формат Binance:
        [
          {
            "e": "24hrMiniTicker",  // Event type
            "E": 123456789,         // Event time
            "s": "BTCUSDT",         // Symbol
            "c": "0.0025",          // Close price
            "o": "0.0010",          // Open price
            "h": "0.0025",          // High price
            "l": "0.0010",          // Low price
            "v": "10000",           // Total traded base asset volume
            "q": "18"               // Total traded quote asset volume
          }
        ]
        """
        for ticker in data:
            symbol = ticker['s']
            
            # Фильтруем мусор: берем только USDT пары
            if not symbol.endswith('USDT'):
                continue
                
            price = float(ticker['c'])
            # Рассчитываем изменение % сами (или берем Open и Close)
            open_price = float(ticker['o'])
            change_pct = ((price - open_price) / open_price) * 100 if open_price else 0
            
            # Если монеты еще нет в словаре, создаем структуру
            if symbol not in self.prices:
                self.prices[symbol] = {
                    "symbol": symbol,
                    "price": price,
                    "change_24h": change_pct,
                    "volume": float(ticker['q']),
                    "rsi": None,   # Placeholder
                    "trend": None  # Placeholder
                }
            else:
                # Если есть, обновляем только рыночные данные, сохраняя RSI/Trend
                self.prices[symbol].update({
                    "price": price,
                    "change_24h": change_pct,
                    "volume": float(ticker['q'])
                })

    def get_all_tickers(self):
        """Возвращает список всех монет отсортированный по объему"""
        # Превращаем dict в list
        data = list(self.prices.values())
        # Сортируем по объему (desc)
        data.sort(key=lambda x: x['volume'], reverse=True)
        return data

market_manager = MarketDataManager()
