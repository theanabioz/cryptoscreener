import tvscreener as tv

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        # Инициализируем скринер для криптовалют
        cs = tv.CryptoScreener()
        
        # Фильтр: Только Binance и пары к USDT (для простоты MVP)
        # В версии 0.2.x методы могут называться иначе, но попробуем стандартные.
        # Если set_exchange не сработает, нужно будет искать другой способ фильтрации.
        # Но пока проблема была только в импорте Column.
        cs.set_exchange('BINANCE')
        cs.set_symbol_search('USDT') 
        
        # Сортировка по объему
        cs.sort_by('volume', ascending=False)
        
        # Получаем данные
        df = cs.get(limit=limit, print_request=False)
        
        # Преобразуем DataFrame в список словарей
        data = df.to_dict(orient='records')
        
        return self._normalize_data(data)

    def _normalize_data(self, raw_data: list):
        """
        Приводим данные TradingView к нашему формату Frontend (Coin interface)
        """
        normalized = []
        for item in raw_data:
            coin = {
                "id": item.get('symbol', '').split('USDT')[0].lower(), # BTCUSDT -> btc
                "symbol": item.get('symbol', '').replace('BINANCE:', ''),
                "name": item.get('description', item.get('symbol')), 
                "current_price": item.get('close') or item.get('price'),
                "price_change_percentage_24h": item.get('change') or item.get('change_abs'),
                "market_cap": item.get('market_cap_basic'),
                "total_volume": item.get('volume'),
                "image": f"https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"
            }
            normalized.append(coin)
            
        return normalized
