import os, time
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="NSE Top 10", page_icon="📊", layout="wide")
DB_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DB_URL, pool_pre_ping=True)

st.title("📊 Top 10 to Buy — NSE Screener")
st.caption("Session VWAP • EMA20 • RSI14 • Gap% • RelVol")

@st.cache_data(ttl=15)
def load(name: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {name} ORDER BY id DESC LIMIT 500", engine)

df = load("top10_buy_view") if DB_URL else pd.DataFrame()
if df.empty:
    st.info("No BUY candidates yet — waiting for worker…")
else:
    st.dataframe(df[["ticker","company","decision","score","rsi14","ema20","vwap","close"]], use_container_width=True)

st.divider()
watch = load("watchlist_view") if DB_URL else pd.DataFrame()
if not watch.empty:
    st.dataframe(watch[["ticker","company","gap_pct","relvol"]], use_container_width=True)
