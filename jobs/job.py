import os
from sqlalchemy import create_engine, text
engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
job = os.getenv("JOB_NAME", "preopen-scan")
with engine.begin() as conn:
    if job == "eod-cleanup":
        conn.execute(text("DELETE FROM top10_buy WHERE ts < NOW() - INTERVAL '15 days'"))
        conn.execute(text("DELETE FROM snapshots WHERE ts < NOW() - INTERVAL '7 days'"))
    else:
        pass
print(f"[OK] Cron job completed: {job}")
