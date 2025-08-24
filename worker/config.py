import os
class Config:
    DB_URL = os.environ["DATABASE_URL"]
    PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
    SCAN_INTERVAL_SEC = int(os.getenv("SCAN_INTERVAL_SEC", "60"))
    SYMBOLS = os.getenv("SYMBOLS", "RELIANCE,TCS,HDFCBANK,ICICIBANK,INFY,SBIN").split(",")
    VWAP_MODE = os.getenv("VWAP_MODE", "session")  # session|cumulative
    DATA_PROVIDER = os.getenv("DATA_PROVIDER", "YAHOO")  # YAHOO | ZERODHA_WS
    # Zerodha
    ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
    ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
    ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")
    ZERODHA_PRODUCT = os.getenv("ZERODHA_PRODUCT", "MIS")  # MIS|CNC
    ZERODHA_EXCHANGE = os.getenv("ZERODHA_EXCHANGE", "NSE")  # NSE|BSE
    # Kill switch defaults
    KS_MAX_DAILY_LOSS = float(os.getenv("KS_MAX_DAILY_LOSS", "-5000"))  # INR
    KS_MAX_CONSEC_ERRORS = int(os.getenv("KS_MAX_CONSEC_ERRORS", "10"))
    KS_MAX_TRADES_PER_MIN = int(os.getenv("KS_MAX_TRADES_PER_MIN", "120"))
    KS_HEARTBEAT_TIMEOUT = int(os.getenv("KS_HEARTBEAT_TIMEOUT", "90"))  # seconds
