from typing import Dict, List
import pandas as pd
from kiteconnect import KiteConnect, KiteTicker

def resolve_tokens(kite: KiteConnect, symbols: List[str]) -> Dict[str, int]:
    tokens = {}
    instruments = kite.instruments("NSE")
    name_to_token = {row["tradingsymbol"].upper(): row["instrument_token"] for row in instruments}
    for s in symbols:
        key = s.upper()
        if key.endswith(".NS"): key = key[:-3]
        if key in name_to_token:
            tokens[s] = name_to_token[key]
    return tokens

class TickerClient:
    def __init__(self, api_key: str, access_token: str, symbols: List[str]):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.symbols = symbols
        self.token_map = resolve_tokens(self.kite, symbols)
        self.ws = KiteTicker(api_key, access_token)
        self.buffers: Dict[str, list] = {f"{s}.NS" if not s.endswith(".NS") else s: [] for s in symbols}

        def on_ticks(ws, ticks):
            for t in ticks:
                tok = t.get("instrument_token")
                last = t.get("last_price")
                vol = t.get("volume", 0)
                sym = next((k for k,v in self.token_map.items() if v==tok), None)
                if not sym: continue
                symns = f"{sym}.NS" if not sym.endswith(".NS") else sym
                self.buffers[symns].append((pd.Timestamp.utcnow(), last, vol))

        def on_connect(ws, resp):
            ws.subscribe(list(self.token_map.values()))
            ws.set_mode(ws.MODE_LTP, list(self.token_map.values()))

        self.ws.on_ticks = on_ticks
        self.ws.on_connect = on_connect

    def start(self):
        self.ws.connect(threaded=True)

    def fetch_recent_frame(self, symbol: str, bars: int = 60) -> pd.DataFrame:
        symns = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
        data = list(self.buffers.get(symns, []))[-bars*20:]
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data, columns=["ts","ltp","vol"]).set_index("ts").sort_index()
        o = df["ltp"].resample("15min").first()
        h = df["ltp"].resample("15min").max()
        l = df["ltp"].resample("15min").min()
        c = df["ltp"].resample("15min").last()
        v = df["vol"].resample("15min").sum()
        out = pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v}).dropna()
        return out.tail(bars)
