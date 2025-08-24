from strategies.momentum_vwap import evaluate, Inputs

def score_signal(sig: dict) -> dict:
    out = evaluate(Inputs(
        close=sig["close"], ema20=sig["ema20"], vwap=sig["vwap"], rsi14=sig["rsi14"],
        relvol=sig.get("relvol"), gap_pct=sig.get("gap_pct")
    ))
    return {"score": out.score, "decision": out.decision, "reasons": out.reasons}
