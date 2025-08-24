import time
from dataclasses import dataclass, field
from collections import deque

@dataclass
class KillSwitchConfig:
    max_daily_loss: float = -5000.0
    max_consec_errors: int = 10
    max_trades_per_min: int = 120
    heartbeat_timeout_sec: int = 90

@dataclass
class KillSwitch:
    cfg: KillSwitchConfig
    tripped: bool = False
    last_heartbeat_ts: float = field(default_factory=lambda: time.time())
    consec_errors: int = 0
    trade_times: deque = field(default_factory=lambda: deque(maxlen=1000))

    def heartbeat(self):
        self.last_heartbeat_ts = time.time()

    def record_trade(self):
        self.trade_times.append(time.time())

    def record_error(self):
        self.consec_errors += 1

    def reset_errors(self):
        self.consec_errors = 0

    def _trades_last_min(self) -> int:
        now = time.time()
        while self.trade_times and now - self.trade_times[0] > 60:
            self.trade_times.popleft()
        return len(self.trade_times)

    def check(self, day_pnl: float | None = None) -> tuple[bool, str]:
        if self.tripped:
            return True, "Already tripped"
        now = time.time()
        if now - self.last_heartbeat_ts > self.cfg.heartbeat_timeout_sec:
            self.tripped = True; return True, "Heartbeat timeout"
        if self.consec_errors >= self.cfg.max_consec_errors:
            self.tripped = True; return True, "Too many consecutive errors"
        if self._trades_last_min() > self.cfg.max_trades_per_min:
            self.tripped = True; return True, "Trade rate exceeded"
        if day_pnl is not None and day_pnl <= self.cfg.max_daily_loss:
            self.tripped = True; return True, f"Max daily loss breached ({day_pnl})"
        return False, ""

    def maybe_trip_and_flatten(self, broker, day_pnl: float | None = None):
        tripped, reason = self.check(day_pnl)
        if tripped:
            print(f"[KILL] KillSwitch tripped: {reason}. Flattening positions…")
            try:
                broker.flatten_all()
            finally:
                return True, reason
        return False, ""
