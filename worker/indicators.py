import numpy as np, pandas as pd

def ema(s: pd.Series, length: int) -> pd.Series:
    return s.ewm(span=length, adjust=False, min_periods=length).mean()

def rsi(s: pd.Series, length: int = 14) -> pd.Series:
    d = s.diff(); gain = d.clip(lower=0); loss = -d.clip(upper=0)
    ag = gain.ewm(alpha=1/length, adjust=False, min_periods=length).mean()
    al = loss.ewm(alpha=1/length, adjust=False, min_periods=length).mean()
    rs = ag / al
    r = 100 - (100 / (1 + rs))
    r = r.where(~((al==0)&(ag>0)), 100.0)
    r = r.where(~((ag==0)&(al>0)), 0.0)
    r = r.where(~((ag==0)&(al==0)), 50.0)
    return r.fillna(50)

def vwap_session(h, l, c, v):
    tp = (h + l + c) / 3.0
    dates = c.index.date
    return (tp*v).groupby(dates).cumsum() / v.groupby(dates).cumsum()
