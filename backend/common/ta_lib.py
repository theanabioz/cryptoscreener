import pandas as pd
import numpy as np

def calculate_all_indicators(df):
    """Рассчитывает массив индикаторов (The Beast) на чистом Pandas/Numpy."""
    # Убеждаемся, что данные числовые
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float)
    
    res = {}

    # 1. RSI (Momentum)
    for p in [7, 14, 21]:
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
        rs = gain / loss
        res[f'rsi_{p}'] = (100 - (100 / (1 + rs))).iloc[-1]

    # 2. MACD (Trend)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    res['macd'] = macd.iloc[-1]
    res['macd_signal'] = signal.iloc[-1]
    res['macd_hist'] = (macd - signal).iloc[-1]

    # 3. EMA Grid (Trend)
    for p in [20, 50, 100, 200]:
        res[f'ema_{p}'] = close.ewm(span=p, adjust=False).mean().iloc[-1]

    # 4. Bollinger Bands (Volatility)
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    res['bb_upper'] = (sma20 + (std20 * 2)).iloc[-1]
    res['bb_lower'] = (sma20 - (std20 * 2)).iloc[-1]
    res['bb_middle'] = sma20.iloc[-1]

    # 5. ATR (Volatility)
    tr = pd.concat([high - low, 
                    (high - close.shift()).abs(), 
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    res['atr_14'] = tr.rolling(window=14).mean().iloc[-1]

    # 6. Stochastic (Momentum)
    low14 = low.rolling(window=14).min()
    high14 = high.rolling(window=14).max()
    k = 100 * (close - low14) / (high14 - low14)
    res['stoch_k'] = k.iloc[-1]
    res['stoch_d'] = k.rolling(window=3).mean().iloc[-1]

    # 7. ADX (Trend Strength)
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    tr_rolling = tr.rolling(window=14).sum()
    plus_di = 100 * (plus_dm.rolling(window=14).sum() / tr_rolling)
    minus_di = 100 * (minus_dm.abs().rolling(window=14).sum() / tr_rolling)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    res['adx_14'] = dx.rolling(window=14).mean().iloc[-1]

    # 8. MFI (Money Flow Index - Volume)
    tp = (high + low + close) / 3
    mf = tp * volume
    pos_mf = mf.where(tp > tp.shift(1), 0).rolling(window=14).sum()
    neg_mf = mf.where(tp < tp.shift(1), 0).rolling(window=14).sum()
    mfr = pos_mf / neg_mf
    res['mfi_14'] = (100 - (100 / (1 + mfr))).iloc[-1]

    # Очистка от NaN
    return {k: (round(float(v), 6) if v is not None and not np.isnan(v) else None) for k, v in res.items()}