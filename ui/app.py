import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL) if DB_URL else None

@st.cache_data(ttl=60)
def load(name: str):
    if engine is None:
        return pd.DataFrame()
    return pd.read_sql(f"SELECT * FROM {name} ORDER BY id DESC LIMIT 500", engine)

# 🔧 Normalize columns (map symbol → ticker if needed)
def normalize_cols(df):
    if df is None or df.empty:
        return df
    if "ticker" not in df.columns and "symbol" in df.columns:
        df = df.rename(columns={"symbol": "ticker"})
    for col in ["rsi14", "ema20", "vwap", "close", "score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# Load data
df = load("top10_buy_view") if DB_URL else pd.DataFrame()
watch = load("watchlist_view") if DB_URL else pd.DataFrame()

# Normalize
df = normalize_cols(df)
watch = normalize_cols(watch)

st.set_page_config(page_title="📊 Top 10 to Buy — NSE Screener", layout="wide")

st.title("📊 Top 10 to Buy — NSE Screener")
st.caption("Session VWAP • EMA20 • RSI14 • Gap% • RelVol")

# --- Top 10 BUY ---
st.subheader("Top 10 BUY Candidates")
cols_main = [c for c in ["ticker","company","decision","score","rsi14","ema20","vwap","close"] if c in df.columns]
if cols_main:
    st.dataframe(df[cols_main], use_container_width=True)
else:
    st.info("No BUY candidates yet — waiting for worker…")

# --- Watchlist ---
st.subheader("Watchlist")
cols_watch = [c for c in ["ticker","company","reason","price","rsi14","ema20","vwap","note"] if c in watch.columns]
if cols_watch:
    st.dataframe(watch[cols_watch], use_container_width=True)
else:
    st.info("No watchlist data yet.")
