import tvscreener as tv
import pandas as pd
import math
import time

class ScreenerService:
    def __init__(self):
        self._cached_data = None
        self._last_update = 0
        self._cache_ttl = 1.0 # 1 second cache

    def get_crypto_screener(self, limit: int = 50):
        # Проверка кэша
        now = time.time()
        if self._cached_data and (now - self._last_update) < self._cache_ttl:
            return self._cached_data

        try:
            cs = tv.CryptoScreener()
            df = cs.get()
            
            if df is None or df.empty:
                return []

            # --- ОЧИСТКА ДАННЫХ В PANDAS ---
            # 1. Только Binance (если есть колонка)
            if 'Exchange' in df.columns:
                df = df[df['Exchange'] == 'BINANCE']
            
            # 2. Только пары к USDT и фильтрация фьючерсов
            if 'Symbol' in df.columns:
                df = df[df['Symbol'].str.contains('USDT', na=False)]
                # Убираем .P (Perpetual)
                df = df[~df['Symbol'].str.contains(r'\.P$', na=False)] 
            
            # 3. Сортировка по объему
            vol_col = 'Volume' if 'Volume' in df.columns else 'Average Volume (10 day)'
            if vol_col in df.columns:
                df = df.sort_values(by=vol_col, ascending=False)

            # Берем топ-N записей ПОСЛЕ ВСЕХ ФИЛЬТРОВ
            df_limited = df.head(limit)
            
            # Конвертируем в dict
            data = df_limited.to_dict(orient='records')
            
            result = self._normalize_data(data)
            
            # Сохраняем в кэш
            self._cached_data = result
            self._last_update = time.time()
            
            return result
        except Exception as e:
            print(f"TVScreener Error: {e}")
            return []

    def _normalize_data(self, raw_data: list):
        normalized = []
        for item in raw_data:
            try:
                def clean_float(val):
                    try:
                        f_val = float(val)
                        if math.isnan(f_val) or math.isinf(f_val): return 0
                        return f_val
                    except: return 0

                def get_val(keys_list):
                    for k in keys_list:
                        if k in item: return item[k]
                        for item_key in item.keys():
                            if item_key.lower() == k.lower(): return item[item_key]
                    return None

                symbol_raw = get_val(['Symbol', 'symbol']) or 'Unknown'
                ticker = symbol_raw
                
                # Если в символе есть биржа (BINANCE:BTCUSDT), убираем её
                if ':' in str(symbol_raw):
                    ticker = symbol_raw.split(':')[1]
                
                # Имя монеты (убираем "TetherUS" из названия если оно есть)
                name = get_val(['Description', 'description', 'Name']) or ticker
                display_name = name.split('/')[0].strip() if '/' in name else name

                coin = {
                    "id": ticker.replace('USDT', '').lower(),
                    "symbol": ticker.replace('USDT', ''), # Для отображения лучше просто BTC
                    "name": display_name, 
                    "current_price": clean_float(get_val(['close', 'Close', 'Ask', 'last', 'Price'])),
                    "price_change_percentage_24h": clean_float(get_val(['Change %', 'change', 'Change'])),
                    "market_cap": clean_float(get_val(['market_cap_basic', 'Market Cap', 'Fully Diluted Market Cap'])),
                    "total_volume": clean_float(get_val(['volume', 'Volume', 'Average Volume (10 day)'])),
                    "image": f"https://assets.coincap.io/assets/icons/{ticker.replace('USDT', '').lower()}@2x.png" 
                }
                normalized.append(coin)
            except Exception as parse_error:
                print(f"Error parsing row: {parse_error}")
                continue
            
        return normalized
