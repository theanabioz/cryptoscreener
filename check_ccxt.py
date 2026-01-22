import ccxt
import json

ex = ccxt.binance()
markets = ex.load_markets()

# Найдем BTC/USDT для примера
btc = markets.get('BTC/USDT')

if btc:
    print(json.dumps(btc, indent=2))
else:
    print("BTC/USDT not found")
