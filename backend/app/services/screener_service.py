import tvscreener as tv
import pandas as pd

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        try:
            # Инициализируем скринер
            cs = tv.CryptoScreener()
            
            # Получаем все данные (библиотека сама решает сколько вернуть по умолчанию)
            df = cs.get()
            
            # Если вернулось пустое значение или не DataFrame
            if df is None or df.empty:
                return []

            # Берем топ-N записей
            df_limited = df.head(limit)
            
            # Преобразуем в список словарей
            data = df_limited.to_dict(orient='records')
            
            return self._normalize_data(data)
        except Exception as e:
            print(f"TVScreener Error: {e}")
            # Fallback или пустой список, чтобы сервер не падал
            return []

    def _normalize_data(self, raw_data: list):
        normalized = []
        for item in raw_data:
            try:
                # DEBUG: Print raw item to see available keys in logs
                print(f"Raw item keys: {item.keys()}", flush=True)
                
                # Пытаемся безопасно достать данные.
                # В 0.2.0 колонки могут называться иначе, поэтому используем .get() с дефолтами
                
                symbol_raw = item.get('symbol', 'Unknown')
                # Очищаем тикер (обычно приходит BINANCE:BTCUSDT)
                if ':' in symbol_raw:
                    ticker = symbol_raw.split(':')[1]
                else:
                    ticker = symbol_raw
                
                # Убираем USDT для красивого ID
                coin_id = ticker.replace('USDT', '').lower()
                
                coin = {
                    "id": coin_id,
                    "symbol": ticker,
                    "name": item.get('description', ticker), 
                    "current_price": item.get('close') or item.get('price', 0),
                    "price_change_percentage_24h": item.get('change', 0),
                    "market_cap": item.get('market_cap_basic', 0),
                    "total_volume": item.get('volume', 0),
                    # Генерируем логотип на основе символа
                    "image": f"https://s2.coinmarketcap.com/static/img/coins/64x64/1.png" 
                }
                normalized.append(coin)
            except Exception as parse_error:
                print(f"Error parsing row: {parse_error}")
                continue
            
        return normalized
