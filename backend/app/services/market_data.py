import asyncio
import json
import logging
import websockets
import pandas as pd
import ta
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
            cls._instance.candles: Dict[str, pd.DataFrame] = {}
            cls._instance.symbol_names: Dict[str, str] = {} # Храним полные имена
            cls._instance.running = False
        return cls._instance

    async def fetch_full_names(self):
        """Один раз загружаем соответствие тикеров и полных имен"""
        try:
            import ccxt.async_support as ccxt_lib
            ex = ccxt_lib.binance()
            markets = await ex.fetch_markets()
            for m in markets:
                if m['quote'] == 'USDT':
                    # Пытаемся достать имя из info или использовать base
                    # У Binance info обычно содержит 'baseAsset'
                    self.symbol_names[m['symbol']] = m['baseId'] # BTC, ETH... 
                    # Для более красивых имен можно будет потом подключить CoinGecko
            await ex.close()
            logger.info(f"Loaded {len(self.symbol_names)} full names from Binance")
        except Exception as e:
            logger.error(f"Error fetching full names: {e}")

    async def start_stream(self):
        """Запускает WebSocket соединение с Binance"""
        # Сначала грузим имена
        await self.fetch_full_names()
        
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
        for ticker in data:
            symbol = ticker['s']
            if not symbol.endswith('USDT'): continue
                
            price = float(ticker['c'])
            open_price = float(ticker['o'])
            change_pct = ((price - open_price) / open_price) * 100 if open_price else 0
            
            # 1. Базовое обновление цены
            if symbol not in self.prices:
                name = self.symbol_names.get(symbol, symbol.replace('USDT', ''))
                self.prices[symbol] = {
                    "symbol": symbol.replace('USDT', ''),
                    "name": name,
                    "price": price,
                    "change_24h": change_pct,
                    "volume": float(ticker['q']),
                    "rsi": None,
                    "macd": None,
                    "ema50": None,
                    "bb_pos": None,
                    "trend": None
                }
            else:
                self.prices[symbol].update({
                    "price": price,
                    "change_24h": change_pct,
                    "volume": float(ticker['q'])
                })

            # 2. Real-time TA calculation
            # Если у нас есть история свечей для этой монеты (загруженная воркером)
            if symbol in self.candles:
                df = self.candles[symbol]
                
                # Обновляем последнюю свечу текущей ценой
                # (В упрощенном виде мы просто меняем Close у последней свечи)
                # Для полноценной логики нужно проверять время закрытия свечи,
                # но для 1h таймфрейма внутри часа это корректная аппроксимация.
                last_idx = df.index[-1]
                df.at[last_idx, 'close'] = price
                df.at[last_idx, 'high'] = max(df.at[last_idx, 'high'], price)
                df.at[last_idx, 'low'] = min(df.at[last_idx, 'low'], price)
                
                # Пересчитываем RSI (достаточно пересчитать только хвост, но ta считает векторно)
                # Чтобы было быстро, можно брать последние 50 строк
                try:
                    # RSI 14
                    rsi = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
                    
                    # EMA 50
                    ema50 = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
                    
                    self.prices[symbol].update({
                        "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                        "trend": "Bullish" if price > ema50 else "Bearish"
                    })
                except Exception:
                    pass

    def get_all_tickers(self):
        data = list(self.prices.values())
        data.sort(key=lambda x: x['volume'], reverse=True)
        return data

market_manager = MarketDataManager()
