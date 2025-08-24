from worker.strategies.momentum_vwap import evaluate, Inputs

def test_buy_when_above_ema_vwap_and_rsi_ok():
    out = evaluate(Inputs(close=105, ema20=100, vwap=101, rsi14=55))
    assert out.decision == "BUY" and out.score == 30
