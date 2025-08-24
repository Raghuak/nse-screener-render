from worker.router.throttle import OrderThrottler

def test_per_second_limit():
    t = OrderThrottler(max_per_sec=3, max_per_min=200, max_per_day=3000)
    c=0
    for _ in range(3):
        with t(): c+=1
    assert c==3
