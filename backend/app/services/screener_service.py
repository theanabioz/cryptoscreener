import tvscreener as tv
# Fixed import issue for v0.2.0

class ScreenerService:
    def get_crypto_screener(self, limit: int = 50):
        # Инициализируем скринер
        cs = tv.CryptoScreener()
        
        # В версии 0.2.0 API изменился.
        # Вместо set_exchange используем фильтрацию через where, если она доступна,
        # или просто запрашиваем данные, так как CryptoScreener по умолчанию ищет крипту.
        
        # Попытка 1: Просто получить данные, чтобы проверить работоспособность.
        # Фильтрацию биржи добавим позже, когда разберемся с их API.
        
        # Сортировка
        # cs.sort_by('volume', ascending=False) # Этот метод тоже может отсутствовать
        
        # Получаем данные
        df = cs.get(limit=limit, print_request=False)
        
        data = df.to_dict(orient='records')
        return self._normalize_data(data)

    def _normalize_data(self, raw_data: list):
        normalized = []
        for item in raw_data:
            # Пытаемся безопасно достать данные
            symbol_raw = item.get('symbol', '')
            # Очищаем тикер (обычно приходит BINANCE:BTCUSDT)
            ticker = symbol_raw.split(':')[1] if ':' in symbol_raw else symbol_raw
            
            coin = {
                "id": ticker.replace('USDT', '').lower(),
                "symbol": ticker,
                "name": item.get('description', ticker), 
                "current_price": item.get('close') or item.get('price', 0),
                "price_change_percentage_24h": item.get('change', 0),
                "market_cap": item.get('market_cap_basic', 0),
                "total_volume": item.get('volume', 0),
                "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"
            }
            normalized.append(coin)
            
        return normalized
