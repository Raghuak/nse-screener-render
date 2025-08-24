from kiteconnect import KiteConnect

class Broker:
    def __init__(self, api_key: str, access_token: str, product: str = "MIS", exchange: str = "NSE", paper: bool = False):
        self.paper = paper
        self.product = product.upper()
        self.exchange = exchange.upper()
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def _exch(self):
        return self.kite.EXCHANGE_NSE if self.exchange == "NSE" else self.kite.EXCHANGE_BSE

    def _prod(self):
        return self.kite.PRODUCT_MIS if self.product == "MIS" else self.kite.PRODUCT_CNC

    def place_market_buy(self, symbol: str, qty: int):
        if self.paper:
            print(f"[PAPER] BUY {symbol} x{qty}")
            return {"order_id":"paper-buy"}
        tsym = symbol[:-3] if symbol.endswith(".NS") else symbol
        return self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self._exch(),
            tradingsymbol=tsym,
            transaction_type=self.kite.TRANSACTION_TYPE_BUY,
            quantity=int(qty),
            product=self._prod(),
            order_type=self.kite.ORDER_TYPE_MARKET
        )

    def place_market_sell(self, symbol: str, qty: int):
        if self.paper:
            print(f"[PAPER] SELL {symbol} x{qty}")
            return {"order_id":"paper-sell"}
        tsym = symbol[:-3] if symbol.endswith(".NS") else symbol
        return self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self._exch(),
            tradingsymbol=tsym,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=int(qty),
            product=self._prod(),
            order_type=self.kite.ORDER_TYPE_MARKET
        )

    def flatten_all(self):
        if self.paper:
            print("[PAPER] FLATTEN ALL positions")
            return
        pos = self.kite.positions().get("net", [])
        for p in pos:
            tsym = p["tradingsymbol"]
            exch = p["exchange"]
            qty = p.get("quantity", 0)
            if qty == 0: 
                continue
            if qty > 0:
                self.kite.place_order(
                    variety=self.kite.VARIETY_REGULAR,
                    exchange=exch,
                    tradingsymbol=tsym,
                    transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                    quantity=int(qty),
                    product=self._prod(),
                    order_type=self.kite.ORDER_TYPE_MARKET
                )
            else:
                self.kite.place_order(
                    variety=self.kite.VARIETY_REGULAR,
                    exchange=exch,
                    tradingsymbol=tsym,
                    transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                    quantity=int(abs(qty)),
                    product=self._prod(),
                    order_type=self.kite.ORDER_TYPE_MARKET
                )
