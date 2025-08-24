import pandas as pd, numpy as np

def fetch_intraday(symbol: str, bars: int = 60) -> pd.DataFrame:
    now = pd.Timestamp.utcnow().tz_localize(None)
    idx = pd.date_range(end=now, periods=bars, freq="15min")
    base = 100
    close = pd.Series(base + np.cumsum(np.random.normal(0,0.2,bars)), index=idx)
    high = close + 0.2; low = close - 0.2; vol = pd.Series(1000, index=idx)
    return pd.DataFrame({"Open": close.shift(1).fillna(close.iloc[0]), "High": high, "Low": low, "Close": close, "Volume": vol})
