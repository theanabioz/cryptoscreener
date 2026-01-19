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
                # Получаем список активных тикеров из нашего менеджера (те, что пришли по сокету)
                tickers = list(market_manager.prices.keys())
                
                if not tickers:
                    await asyncio.sleep(5)
                    continue

                # Разбиваем на чанки, чтобы не дудосить API
                chunk_size = 10
                for i in range(0, len(tickers), chunk_size):
                    if not self.running: break
                    
                    chunk = tickers[i:i + chunk_size]
                    tasks = [self.analyze_coin(symbol) for symbol in chunk]
                    
                    # Запускаем пачку параллельно
                    await asyncio.gather(*tasks)
                    
                    # Пауза между пачками (Rate Limit)
                    await asyncio.sleep(1) 
                
                # После полного прохода ждем 5 минут перед следующим обновлением
                # (TA не меняется каждую секунду)
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

            # Конвертируем в DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- РАСЧЕТ ИНДИКАТОРОВ (библиотека ta) ---
            
            # 1. RSI (14)
            rsi = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
            
            # 2. MACD
            macd_obj = ta.trend.MACD(close=df['close'])
            macd = macd_obj.macd().iloc[-1]
            macd_signal = macd_obj.macd_signal().iloc[-1]
            
            # 3. EMA (50, 200) - для тренда
            ema50 = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
            
            # Обновляем данные в Market Manager (добавляем поля TA)
            if symbol in market_manager.prices:
                market_manager.prices[symbol].update({
                    "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                    "macd": round(macd, 4) if not pd.isna(macd) else None,
                    "macd_signal": round(macd_signal, 4) if not pd.isna(macd_signal) else None,
                    "trend": "Bullish" if df['close'].iloc[-1] > ema50 else "Bearish"
                })
                
        except Exception as e:
            # Ошибки часто бывают (нет пары, делистинг), не спамим лог
            # logger.debug(f"Failed to analyze {symbol}: {e}")
            pass

    async def close(self):
        await self.exchange.close()

ta_service = TechnicalAnalysisService()
