import requests
import json
import os
import time

SEC_HEADERS = {
    "User-Agent": "ONYX_Project MVP (contact@onyxproject.com)" 
}

CACHE_DIR = "src/data/cache/sec"

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_company_tickers():
    """Fetches the SEC mapping of tickers to CIKs."""
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=SEC_HEADERS)
    response.raise_for_status()
    return response.json()

def get_cik_for_ticker(ticker: str) -> str:
    """Returns the zero-padded CIK for a given ticker."""
    tickers_data = fetch_company_tickers()
    for entry in tickers_data.values():
        if entry["ticker"] == ticker.upper():
            return str(entry["cik_str"]).zfill(10)
    raise ValueError(f"Ticker {ticker} not found in SEC database.")

def fetch_company_facts(ticker: str) -> dict:
    """Fetches historical financial facts for a company from the SEC EDGAR API."""
    ensure_cache_dir()
    cache_path = os.path.join(CACHE_DIR, f"{ticker.upper()}_facts.json")
    
    # Check cache (1 day expiry for MVP)
    if os.path.exists(cache_path):
        if time.time() - os.path.getmtime(cache_path) < 86400:
            with open(cache_path, "r") as f:
                return json.load(f)

    # Fetch from API
    try:
        cik = get_cik_for_ticker(ticker)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        response = requests.get(url, headers=SEC_HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Save to cache
        with open(cache_path, "w") as f:
            json.dump(data, f)
            
        return data
    except Exception as e:
        print(f"Error fetching SEC data for {ticker}: {e}")
        return {} # Graceful degradation
