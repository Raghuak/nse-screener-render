from dataclasses import dataclass

@dataclass
class Inputs:
    close: float; ema20: float; vwap: float; rsi14: float
    relvol: float | None = None; gap_pct: float | None = None

@dataclass
class Output:
    score: int; decision: str; reasons: list[str]

BUY_THRESHOLD = 20

def evaluate(x: Inputs) -> Output:
    score, reasons = 0, []
    if x.close > x.ema20: score += 10; reasons.append("Above EMA20")
    if x.close > x.vwap:  score += 10; reasons.append("Above VWAP")
    if x.rsi14 <= 60:     score += 10; reasons.append("RSI<=60")
    decision = "BUY" if score >= BUY_THRESHOLD else "WATCH"
    return Output(score, decision, reasons)
