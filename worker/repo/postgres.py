from sqlalchemy import create_engine, text

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS snapshots (
  id BIGSERIAL PRIMARY KEY, ts TIMESTAMP DEFAULT NOW(),
  symbol TEXT, close NUMERIC, ema20 NUMERIC, rsi14 NUMERIC, vwap NUMERIC,
  above_ema BOOLEAN, above_vwap BOOLEAN);
CREATE TABLE IF NOT EXISTS top10_buy (
  id BIGSERIAL PRIMARY KEY, ts TIMESTAMP DEFAULT NOW(),
  ticker TEXT, company TEXT, decision TEXT, score INT,
  rsi14 NUMERIC, ema20 NUMERIC, vwap NUMERIC, close NUMERIC);
CREATE TABLE IF NOT EXISTS watchlist (
  id BIGSERIAL PRIMARY KEY, ts TIMESTAMP DEFAULT NOW(),
  ticker TEXT, company TEXT, gap_pct NUMERIC, relvol NUMERIC);
CREATE OR REPLACE VIEW top10_buy_view AS
  SELECT * FROM (SELECT DISTINCT ON (ticker) * FROM top10_buy ORDER BY ticker, id DESC) t
  ORDER BY score DESC, rsi14 ASC LIMIT 10;
CREATE OR REPLACE VIEW watchlist_view AS
  SELECT * FROM (SELECT DISTINCT ON (ticker) * FROM watchlist ORDER BY ticker, id DESC) t
  ORDER BY gap_pct DESC, relvol DESC LIMIT 10;
"""

class Repo:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, pool_pre_ping=True)
        with self.engine.begin() as c:
            for stmt in SCHEMA_SQL.split(";"):
                if stmt.strip(): c.execute(text(stmt))
    def insert_snapshot(self, s, sig):
        with self.engine.begin() as c:
            c.execute(text("INSERT INTO snapshots(symbol,close,ema20,rsi14,vwap,above_ema,above_vwap)"
                           " VALUES (:s,:c,:e,:r,:v,:ae,:av)"),
                      dict(s=s, c=sig["close"], e=sig["ema20"], r=sig["rsi14"], v=sig["vwap"],
                           ae=sig["above_ema"], av=sig["above_vwap"]))
    def insert_top10(self, rows):
        with self.engine.begin() as c:
            for r in rows:
                c.execute(text("INSERT INTO top10_buy (ticker,company,decision,score,rsi14,ema20,vwap,close)"
                               " VALUES (:ticker,:company,:decision,:score,:rsi14,:ema20,:vwap,:close)"), r)
