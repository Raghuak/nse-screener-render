from config import Config as C
from indicators import ema, rsi, vwap_session
from scoring import score_signal
from router.throttle import OrderThrottler
from router.killswitch import KillSwitch, KillSwitchConfig
from repo.postgres import Repo

# Providers
from data_providers.yahoo import fetch_intraday as yahoo_fetch
from data_providers.zerodha_ws import TickerClient as ZClient

import time

# Choose broker (paper/live)
if C.PAPER_TRADING:
    from broker.zerodha_stub import Broker
    broker = Broker(paper=True)
else:
    from broker.zerodha_live import Broker
    broker = Broker(api_key=C.ZERODHA_API_KEY, access_token=C.ZERODHA_ACCESS_TOKEN,
                    product=C.ZERODHA_PRODUCT, exchange=C.ZERODHA_EXCHANGE, paper=False)

repo = Repo(C.DB_URL)
throttle = OrderThrottler()

ks = KillSwitch(KillSwitchConfig(
    max_daily_loss=C.KS_MAX_DAILY_LOSS,
    max_consec_errors=C.KS_MAX_CONSEC_ERRORS,
    max_trades_per_min=C.KS_MAX_TRADES_PER_MIN,
    heartbeat_timeout_sec=C.KS_HEARTBEAT_TIMEOUT,
))

zclient = None
if C.DATA_PROVIDER.upper() == "ZERODHA_WS":
    assert C.ZERODHA_API_KEY and C.ZERODHA_ACCESS_TOKEN, "Set ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN"
    zclient = ZClient(C.ZERODHA_API_KEY, C.ZERODHA_ACCESS_TOKEN, C.SYMBOLS)
    zclient.start()

def get_day_pnl_or_none():
    try:
        if C.PAPER_TRADING:
            return None
        # A lightweight approximation via Kite positions if available in live
        from broker.zerodha_live import Broker as LiveBroker  # type: ignore
        if isinstance(broker, LiveBroker):
            pos = broker.kite.positions().get("net", [])
            # Zerodha doesn't directly return day PnL in all cases; compute rough PnL if fields exist
            pnl_sum = 0.0
            for p in pos:
                # Prefer 'pnl' if present; else estimate  (skip if not available)
                if "pnl" in p and p["pnl"] is not None:
                    pnl_sum += float(p["pnl"])
            return pnl_sum
    except Exception as e:
        print(f"[WARN] day PnL fetch failed: {e}")
    return None

while True:
    t0 = time.time()
    rows_buy = []
    try:
        for s in C.SYMBOLS:
            # provider heartbeat
            ks.heartbeat()

            if C.DATA_PROVIDER.upper() == "ZERODHA_WS" and zclient:
                df = zclient.fetch_recent_frame(s)
            else:
                df = yahoo_fetch(s)
            if df is None or df.empty or len(df) < 30:
                continue

            e = ema(df["Close"], 20); r = rsi(df["Close"], 14); v = vwap_session(df["High"], df["Low"], df["Close"], df["Volume"])
            last = df.iloc[-1]
            sig = dict(close=float(last["Close"]), ema20=float(e.iloc[-1]), rsi14=float(r.iloc[-1]), vwap=float(v.iloc[-1]),
                       above_ema=bool(last["Close"]>e.iloc[-1]), above_vwap=bool(last["Close"]>v.iloc[-1]))
            repo.insert_snapshot(s, sig)
            sc = score_signal(sig)
            decision, score = sc["decision"], sc["score"]
            rows_buy.append(dict(ticker=f"{s}.NS", company=s, decision=decision, score=score,
                                 rsi14=sig["rsi14"], ema20=sig["ema20"], vwap=sig["vwap"], close=sig["close"]))

        top10 = sorted(rows_buy, key=lambda x: (-x["score"], x["rsi14"]))[:10]
        repo.insert_top10(top10)

        # Kill-switch checks before sending any order
        tripped, reason = ks.maybe_trip_and_flatten(broker, get_day_pnl_or_none())
        if tripped:
            print(f"[HALT] Trading halted: {reason}")
            time.sleep(5)
            continue

        for r in top10:
            if r["decision"] == "BUY":
                with throttle:
                    try:
                        broker.place_market_buy(r["ticker"], qty=1)
                        ks.record_trade()
                    except Exception as e:
                        print(f"[ERR] order failed: {e}")
                        ks.record_error()
                # re-check after each send
                tripped, reason = ks.maybe_trip_and_flatten(broker, get_day_pnl_or_none())
                if tripped:
                    print(f"[HALT] Trading halted mid-batch: {reason}")
                    break

        ks.reset_errors()
    except Exception as loop_err:
        print(f"[LOOP] error: {loop_err}")
        ks.record_error()

    dt = time.time() - t0
    time.sleep(max(1, C.SCAN_INTERVAL_SEC - dt))
