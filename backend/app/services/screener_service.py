import tvscreener as tv
import pandas as pd
import math

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        try:
            cs = tv.CryptoScreener()
            df = cs.get()
            
            if df is None or df.empty:
                return []

            # Ограничиваем выборку
            df_limited = df.head(limit)
            
            # Конвертируем в dict
            data = df_limited.to_dict(orient='records')
            
            return self._normalize_data(data)
        except Exception as e:
            print(f"TVScreener Error: {e}")
            return []

    def _normalize_data(self, raw_data: list):
        normalized = []
        for item in raw_data:
            try:
                # Helper для очистки числовых значений (NaN/Inf -> 0)
                def clean_float(val):
                    try:
                        f_val = float(val)
                        if math.isnan(f_val) or math.isinf(f_val):
                            return 0
                        return f_val
                    except:
                        return 0

                # Helper для поиска значения по ключу без учета регистра
                def get_val(keys_list):
                    for k in keys_list:
                        if k in item: return item[k]
                        for item_key in item.keys():
                            if item_key.lower() == k.lower():
                                return item[item_key]
                    return None

                # Достаем данные используя известные ключи из логов
                symbol_raw = get_val(['Symbol', 'symbol']) or 'Unknown'
                
                # Очистка тикера (BINANCE:BTCUSDT -> BTC)
                if ':' in str(symbol_raw):
                    ticker = symbol_raw.split(':')[1]
                else:
                    ticker = str(symbol_raw)
                
                # Удаляем USDT для ID
                coin_id = ticker.replace('USDT', '').lower()
                
                # Собираем монету с очисткой чисел
                coin = {
                    "id": coin_id,
                    "symbol": ticker,
                    "name": get_val(['Description', 'description', 'name']) or ticker, 
                    "current_price": clean_float(get_val(['close', 'Close', 'Ask', 'last', 'Price'])),
                    "price_change_percentage_24h": clean_float(get_val(['Change %', 'change', 'Change'])),
                    "market_cap": clean_float(get_val(['market_cap_basic', 'Market Cap', 'Fully Diluted Market Cap'])),
                    "total_volume": clean_float(get_val(['volume', 'Volume', 'Average Volume (10 day)'])),
                    "image": f"https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"
                }
                normalized.append(coin)
            except Exception as parse_error:
                print(f"Error parsing row: {parse_error}")
                continue
            
        return normalized
