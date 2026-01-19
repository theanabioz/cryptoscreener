# TVScreener v0.2.0 Documentation Reference

## Initialization
```python
from tvscreener import CryptoScreener
cs = CryptoScreener()
```

## Data Retrieval
```python
df = cs.get()
# Returns a Pandas DataFrame
```

## Columns (Common for Crypto)
The library fetches default columns if not specified.
Common column names (might be lowercase or specific):
- `symbol` (e.g. "BINANCE:BTCUSDT")
- `close` (Current Price)
- `change` (24h Change %)
- `volume` (24h Volume)
- `market_cap_basic` (Market Cap)
- `description` (Name, e.g. "Bitcoin")

## Filtering (v0.2.0)
Uses `where` clause.
```python
# Example:
# cs.where(Column('close') > 50000)
```
BUT! For now we are just fetching all.

## Troubleshooting
If columns are missing or named differently, inspect `df.columns`.
