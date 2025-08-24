import time
from worker.router.killswitch import KillSwitch, KillSwitchConfig

def test_killswitch_trade_rate():
    ks = KillSwitch(KillSwitchConfig(max_trades_per_min=3))
    for _ in range(4):
        ks.record_trade()
    tripped, reason = ks.check()
    assert tripped and "Trade rate" in reason
