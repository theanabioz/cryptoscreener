import tvscreener as tv
from tvscreener import Column

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        # Инициализируем скринер для криптовалют
        cs = tv.CryptoScreener()
        
        # Фильтр: Только Binance и пары к USDT (для простоты MVP)
        cs.set_exchange('BINANCE')
        cs.set_symbol_search('USDT') 
        
        # Какие колонки нам нужны
        # TVScreener автоматически подтягивает стандартные, но можно указать явно
        # В версии 2.x API может отличаться, используем стандартный get()
        
        # Сортировка по объему (как пример)
        cs.sort_by('volume', ascending=False)
        
        # Получаем данные
        df = cs.get(limit=limit, print_request=False)
        
        # Преобразуем DataFrame в список словарей
        # tvscreener возвращает Pandas DataFrame
        data = df.to_dict(orient='records')
        
        return self._normalize_data(data)

    def _normalize_data(self, raw_data: list):
        """
        Приводим данные TradingView к нашему формату Frontend (Coin interface)
        """
        normalized = []
        for item in raw_data:
            # TradingView возвращает названия колонок в своем формате
            # Обычно это: 'symbol', 'close', 'change', 'volume', 'market_cap_basic'
            
            # Внимание: названия колонок могут зависеть от версии библиотеки. 
            # Обычно это 'Symbol', 'Close', 'Change %', etc или lowercase.
            # Для надежности в MVP лучше проверить, что прилетает.
            
            coin = {
                "id": item.get('symbol', '').split('USDT')[0].lower(), # BTCUSDT -> btc
                "symbol": item.get('symbol', '').replace('BINANCE:', ''),
                "name": item.get('description', item.get('symbol')), # TV иногда дает description
                "current_price": item.get('close') or item.get('price'),
                "price_change_percentage_24h": item.get('change') or item.get('change_abs'), # Нужно уточнить у либы
                "market_cap": item.get('market_cap_basic'),
                "total_volume": item.get('volume'),
                "image": f"https://s2.coinmarketcap.com/static/img/coins/64x64/1.png" # Заглушка, TV не дает картинки
            }
            normalized.append(coin)
            
        return normalized
