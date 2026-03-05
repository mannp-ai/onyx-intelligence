import yfinance as yf
import pandas as pd
import json
import os
import time

CACHE_DIR = "src/data/cache/stock"

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_stock_history(ticker: str) -> dict:
    """Fetches 5 years of OHLCV data using yfinance."""
    ensure_cache_dir()
    cache_path = os.path.join(CACHE_DIR, f"{ticker.upper()}_stock.json")

    # Check cache (1 day expiry)
    if os.path.exists(cache_path):
        # Only use cache if it was modified within the last 24 hours AND data is not empty
        try:
            if time.time() - os.path.getmtime(cache_path) < 86400:
                with open(cache_path, "r") as f:
                    cached = json.load(f)
                    if cached and "history" in cached and len(cached["history"]) > 0:
                        return cached
        except (json.JSONDecodeError, KeyError):
            pass # Fall through to fetch new data

    try:
        stock = yf.Ticker(ticker)
        # 5 years, monthly for broad trends, proxy for volatility
        hist = stock.history(period="5y", interval="1mo")
        
        if hist.empty:
            return {}

        # Convert index to str
        hist.index = hist.index.strftime('%Y-%m-%d')
        
        # Fundamental data as fallback for non-US stocks
        def extract_fundamentals(df) -> dict:
            if df is None or df.empty: return {}
            # convert df to dict, replace nan with 0.0
            d = df.to_dict()
            clean = {}
            for k, v in d.items():
                date_str = str(k)[:10]
                clean[date_str] = {}
                for ik, iv in v.items():
                    clean[date_str][str(ik)] = float(iv) if pd.notna(iv) else 0.0
            return clean

        bs_clean = extract_fundamentals(stock.balance_sheet)
        inc_clean = extract_fundamentals(stock.income_stmt)
        cf_clean = extract_fundamentals(stock.cashflow)

        data = {
            "ticker": ticker.upper(),
            "info": stock.info, # Includes Beta, P/E, etc.
            "history": json.loads(hist.to_json(orient='index')),
            "fundamentals": {
                "balance_sheet": bs_clean,
                "income_stmt": inc_clean,
                "cash_flow": cf_clean
            }
        }

        with open(cache_path, "w") as f:
            json.dump(data, f)
            
        return data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return {}
