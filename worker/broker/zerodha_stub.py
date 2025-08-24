class Broker:
    def __init__(self, paper=True):
        self.paper = paper
    def place_market_buy(self, symbol: str, qty: int):
        print(f"[PAPER] BUY {symbol} x{qty}")
    def flatten_all(self):
        print("[PAPER] FLATTEN ALL positions")
