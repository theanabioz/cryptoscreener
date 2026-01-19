import tvscreener as tv
import pandas as pd
import math

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        try:
            cs = tv.CryptoScreener()
            
            # Пытаемся применить фильтры для очистки списка
            # В версии 0.2.0 фильтры задаются так (согласно доке и логам):
            try:
                # Фильтруем BINANCE и пары USDT
                # Если Column не импортируется, попробуем передать условия как аргументы или использовать внутренние методы
                # Но судя по всему, CryptoScreener по умолчанию и так хорошо работает.
                # Чтобы убрать .P (perpetuals), мы можем просто отфильтровать результат в Pandas
                pass
            except:
                pass

            df = cs.get()
            
            if df is None or df.empty:
                return []

            # --- ОЧИСТКА ДАННЫХ В PANDAS (Надежнее чем сырые фильтры либы) ---
            # 1. Только Binance (если колонка Exchange есть)
            if 'Exchange' in df.columns:
                df = df[df['Exchange'] == 'BINANCE']
            
            # 2. Только пары к USDT и НЕ фьючерсы (убираем те где есть .P или USD)
            if 'Symbol' in df.columns:
                # Оставляем только те что заканчиваются на USDT и не содержат точек/тире (типично для спота)
                df = df[df['Symbol'].str.contains('USDT', na=False)]
                df = df[~df['Symbol'].str.contains('\.|\:', na=False)] # Убираем контракты с точками
            
            # 3. Сортировка по объему (Volume)
            vol_col = 'Volume' if 'Volume' in df.columns else 'Average Volume (10 day)'
            if vol_col in df.columns:
                df = df.sort_values(by=vol_col, ascending=False)

            # Берем топ-N записей
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
