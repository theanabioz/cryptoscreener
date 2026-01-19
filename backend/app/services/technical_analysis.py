import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import logging
import ta
from app.services.market_data import market_manager

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.running = False

    async def start_loop(self):
        """Фоновый цикл обновления индикаторов"""
        self.running = True
        logger.info("Starting Technical Analysis Loop...")
        
        while self.running:
            try:
                tickers = list(market_manager.prices.keys())
                if not tickers:
                    await asyncio.sleep(5)
                    continue

                logger.info(f"Starting TA analysis for {len(tickers)} symbols...")
                
                processed = 0
                chunk_size = 10
                for i in range(0, len(tickers), chunk_size):
                    if not self.running: break
                    
                    chunk = tickers[i:i + chunk_size]
                    tasks = [self.analyze_coin(symbol) for symbol in chunk]
                    await asyncio.gather(*tasks)
                    
                    processed += len(chunk)
                    if processed % 50 == 0:
                        logger.info(f"Processed {processed}/{len(tickers)} symbols...")
                    
                    await asyncio.sleep(1) 
                
                logger.info("Completed TA cycle. Sleeping 5 mins...")
                await asyncio.sleep(300) 

            except Exception as e:
                logger.error(f"TA Loop Error: {e}")
                await asyncio.sleep(10)

    async def analyze_coin(self, symbol: str):
        try:
            # Скачиваем свечи (1h таймфрейм, 100 штук)
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            if not ohlcv: return

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Сохраняем историю свечей в менеджер для Real-time обновлений
            market_manager.candles[symbol] = df

            # Первичный расчет индикаторов
            # 1. RSI (14)
            rsi = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
            
            # 2. MACD (12, 26, 9)
            macd_obj = ta.trend.MACD(close=df['close'])
            macd = macd_obj.macd().iloc[-1]
            macd_signal = macd_obj.macd_signal().iloc[-1]
            
            # 3. EMA (50)
            ema50 = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
            
            # 4. Bollinger Bands (20, 2)
            bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
            # Определяем позицию цены относительно полос (Low/Mid/High)
            bb_pos = "Mid"
            if df['close'].iloc[-1] > bb.bollinger_hband().iloc[-1]: bb_pos = "High"
            elif df['close'].iloc[-1] < bb.bollinger_lband().iloc[-1]: bb_pos = "Low"

            last_price = df['close'].iloc[-1]

            if symbol in market_manager.prices:
                market_manager.prices[symbol].update({
                    "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                    "macd": round(macd, 4) if not pd.isna(macd) else None,
                    "macd_signal": round(macd_signal, 4) if not pd.isna(macd_signal) else None,
                    "ema50": round(ema50, 2) if not pd.isna(ema50) else None,
                    "bb_pos": bb_pos,
                    "trend": "Bullish" if last_price > ema50 else "Bearish"
                })
                
        except Exception as e:
            logger.error(f"Failed to analyze {symbol}: {e}")

    async def close(self):
        await self.exchange.close()

ta_service = TechnicalAnalysisService()
