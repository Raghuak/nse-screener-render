import time
from contextlib import contextmanager
class OrderThrottler:
    def __init__(self, max_per_sec=10, max_per_min=200, max_per_day=3000):
        self.max_per_sec, self.max_per_min, self.max_per_day = max_per_sec, max_per_min, max_per_day
        self._sec_ts, self._min_ts, self._day = [], [], 0
    def _prune(self, now):
        self._sec_ts = [t for t in self._sec_ts if now - t < 1]
        self._min_ts = [t for t in self._min_ts if now - t < 60]
    @contextmanager
    def __call__(self):
        while True:
            now = time.time(); self._prune(now)
            if len(self._sec_ts) < self.max_per_sec and len(self._min_ts) < self.max_per_min and self._day < self.max_per_day:
                self._sec_ts.append(now); self._min_ts.append(now); self._day += 1; break
            time.sleep(0.1)
        try: yield
        finally: pass
