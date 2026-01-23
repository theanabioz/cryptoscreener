import asyncio
import os
import json
import pandas as pd
import pandas_ta as ta
import numpy as np
import logging
from datetime import datetime
import warnings

# Отключаем предупреждения Pandas (Performance)
warnings.filterwarnings("ignore")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(process)d] %(levelname)s: %(message)s')
logger = logging.getLogger("IE-Worker")

class StatefulIndicatorWorker:
    def __init__(self, symbols, db_pool, redis_client):
        self.symbols = symbols
        self.db = db_pool
        self.redis = redis_client
        self.cache = {}  # { 'BTC/USDT': pd.DataFrame }
        self.tf_map = {'1m': '1T', '5m': '5T', '15m': '15T', '1h': '1H', '4h': '4H', '1d': '1D'}
        self.is_ready = False

    async def warm_up(self):
        """Загружает историю для своих монет в память."""
        logger.info(f"🔥 Warming up cache for {len(self.symbols)} symbols...")
        
        # Загружаем пачками, чтобы не убить БД при старте
        batch_size = 20
        for i in range(0, len(self.symbols), batch_size):
            batch = self.symbols[i:i+batch_size]
            await self._load_batch(batch)
        
        self.is_ready = True
        logger.info(f"✅ Cache ready. Tracking {len(self.cache)} active dataframes.")

    async def _load_batch(self, batch):
        symbols_str = ",".join([f"'{s}'" for s in batch])
        # Берем 1000 свечей (достаточно для EMA200 и RSI)
        query = f"""
            SELECT symbol, time, open, high, low, close, volume 
            FROM candles 
            WHERE symbol IN ({symbols_str}) 
              AND time > NOW() - INTERVAL '3 days'
            ORDER BY time ASC
        """
        try:
            rows = await self.db.fetch_all(query)
            if not rows: return

            # Группируем по символам в Python (быстрее, чем N запросов)
            df_all = pd.DataFrame(rows, columns=['symbol', 'time', 'open', 'high', 'low', 'close', 'volume'])
            df_all['time'] = pd.to_datetime(df_all['time'])
            df_all.set_index('time', inplace=True)

            for symbol in batch:
                df = df_all[df_all['symbol'] == symbol]
                if not df.empty:
                    # Храним только нужные колонки и типы
                    self.cache[symbol] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        except Exception as e:
            logger.error(f"Error loading batch: {e}")

    def calculate_ta(self, df):
        """
        Быстрый расчет индикаторов с использованием pandas-ta.
        Рассчитываем только хвост, если возможно (пока полный пересчет, но в памяти это быстро).
        """
        # Копия хвоста для расчетов (нам не нужна вся история 2 года, 500 свечей хватит)
        # Оптимизация: limit=500
        df_calc = df.iloc[-500:].copy() 

        # Настройка стратегии pandas-ta
        # Custom Strategy
        CustomStrategy = ta.Strategy(
            name="Screener Strategy",
            ta=[
                {"kind": "rsi", "length": 14},
                {"kind": "macd"},
                {"kind": "ema", "length": 50},
                {"kind": "ema", "length": 200},
                {"kind": "bbands", "length": 20},
                {"kind": "supertrend"},
            ]
        )
        
        # Запускаем расчет (Multiprocessing внутри pandas-ta отключен через cores=0 для избежания конфликтов)
        df_calc.ta.strategy(CustomStrategy, cores=0)
        
        return df_calc.iloc[-1].to_dict()

    async def process_tick(self, symbol, price, volume):
        """
        Вызывается при обновлении цены.
        1. Обновляет DataFrame в памяти.
        2. Пересчитывает индикаторы для всех ТФ.
        3. Сохраняет результат.
        """
        if symbol not in self.cache:
            return

        df = self.cache[symbol]
        now = pd.Timestamp.now().floor('1min') # Округляем до минуты

        # Обновляем последнюю свечу или добавляем новую
        if now in df.index:
            # Update current candle
            df.at[now, 'close'] = price
            df.at[now, 'high'] = max(df.at[now, 'high'], price)
            df.at[now, 'low'] = min(df.at[now, 'low'], price)
            df.at[now, 'volume'] += volume # Примерно, лучше брать snapshot volume
        else:
            # New candle
            new_row = pd.DataFrame({
                'open': [price], 'high': [price], 'low': [price], 'close': [price], 'volume': [volume]
            }, index=[now])
            self.cache[symbol] = pd.concat([df, new_row])
            # Очистка памяти (держим не более 2000 свечей)
            if len(self.cache[symbol]) > 2000:
                self.cache[symbol] = self.cache[symbol].iloc[-2000:]

        # --- MULTI-TIMEFRAME CALCULATION ---
        results = {}
        base_df = self.cache[symbol]

        # Для скорости считаем только если прошла минута или сильное изменение
        # Но для точности TWA пока считаем всегда (в памяти это < 10мс)
        
        for tf_name, tf_code in self.tf_map.items():
            if tf_name == '1m':
                resampled = base_df
            else:
                resampled = base_df.resample(tf_code).agg({
                    'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
                }).dropna()
            
            if len(resampled) < 30: continue

            ta_res = self.calculate_ta(resampled)
            
            # Форматируем результат
            results[tf_name] = {
                'rsi': ta_res.get('RSI_14'),
                'macd': ta_res.get('MACD_12_26_9'),
                'macd_signal': ta_res.get('MACDs_12_26_9'),
                'macd_hist': ta_res.get('MACDh_12_26_9'),
                'ema_50': ta_res.get('EMA_50'),
                'ema_200': ta_res.get('EMA_200'),
                'bb_upper': ta_res.get('BBU_20_2.0'),
                'bb_lower': ta_res.get('BBL_20_2.0'),
                'trend': ta_res.get('SUPERT_7_3.0')
            }
            
            # Clean NaNs
            for k, v in results[tf_name].items():
                if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                    results[tf_name][k] = None

        # Сохраняем в БД (Batch update был бы лучше, но пока direct)
        # Оптимизация: сохраняем в Redis, а отдельный процесс дампит в БД
        # Для сейчас: пишем напрямую, но асинхронно
        await self._save_to_db(symbol, price, results)

    async def _save_to_db(self, symbol, price, results):
        query = """
            UPDATE coin_status SET 
                updated_at = NOW(), 
                current_price = $1, 
                indicators_1m = $2, 
                indicators_5m = $3, 
                indicators_15m = $4, 
                indicators_1h = $5, 
                indicators_4h = $6, 
                indicators_1d = $7 
            WHERE symbol = $8
        """
        # json.dumps может быть медленным, лучше orjson, но используем стандартный
        try:
            await self.db.execute(query, 
                price,
                json.dumps(results.get('1m')),
                json.dumps(results.get('5m')),
                json.dumps(results.get('15m')),
                json.dumps(results.get('1h')),
                json.dumps(results.get('4h')),
                json.dumps(results.get('1d')),
                symbol
            )
        except Exception as e:
            logger.error(f"DB Save Error {symbol}: {e}")

