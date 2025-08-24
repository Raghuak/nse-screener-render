import pandas as pd
from worker.indicators import ema, rsi, vwap_session

def test_rsi_edges():
    up = pd.Series(range(1,60), dtype=float)
    dn = pd.Series(range(60,1,-1), dtype=float)
    flat = pd.Series([100.0]*60)
    assert rsi(up).iloc[-1] > 70
    assert rsi(dn).iloc[-1] < 30
    assert 45 <= rsi(flat).iloc[-1] <= 55
