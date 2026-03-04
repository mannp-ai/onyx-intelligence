def extract_latest_annual_value(facts_data: dict, concept: str) -> float:
    """Extracts the most recent 10-K value for a specific US-GAAP concept."""
    try:
        us_gaap = facts_data.get("facts", {}).get("us-gaap", {})
        if concept not in us_gaap:
            return 0.0
            
        units = us_gaap[concept].get("units", {})
        # Usually USD, sometimes shares
        primary_unit = list(units.keys())[0] if units else None
        if not primary_unit: return 0.0
        
        entries = units[primary_unit]
        # Filter for 10-K (annual)
        annuals = [e for e in entries if e.get("form") == "10-K"]
        if not annuals:
            # Fallback to 10-Q if no 10-K found
            annuals = [e for e in entries if e.get("form") == "10-Q"]
            
        if not annuals: return 0.0
        
        # Sort by end date descending
        annuals.sort(key=lambda x: x.get("end", ""), reverse=True)
        return float(annuals[0].get("val", 0.0))
        
    except Exception:
        return 0.0

def extract_latest_yfinance_val(fundamentals: dict, key: str) -> float:
    """Extracts the latest fundamental value from yfinance dictionary."""
    if not fundamentals: return 0.0
    sorted_dates = sorted(fundamentals.keys(), reverse=True)
    if not sorted_dates: return 0.0
    latest_date = sorted_dates[0]
    return fundamentals[latest_date].get(key, 0.0)

def normalize_financials(sec_data: dict, stock_data: dict) -> dict:
    """Standardizes disparate API data into a unified schema for the ML engine."""
    
    # Try SEC EDGAR first (US Stocks)
    bs_sec_exists = extract_latest_annual_value(sec_data, "Assets") > 0
    
    if bs_sec_exists or sec_data:
        # Core Balance Sheet Items
        total_assets = extract_latest_annual_value(sec_data, "Assets")
        total_liabilities = extract_latest_annual_value(sec_data, "Liabilities")
        total_equity = extract_latest_annual_value(sec_data, "StockholdersEquity")
        current_assets = extract_latest_annual_value(sec_data, "AssetsCurrent")
        current_liabilities = extract_latest_annual_value(sec_data, "LiabilitiesCurrent")
        
        # Core Income Statement Items
        revenue = extract_latest_annual_value(sec_data, "Revenues") or \
                  extract_latest_annual_value(sec_data, "SalesRevenueNet")
        
        net_income = extract_latest_annual_value(sec_data, "NetIncomeLoss")
        gross_profit = extract_latest_annual_value(sec_data, "GrossProfit")
    else:
        # Fallback to globally compatible yfinance data (e.g. Indian Stocks)
        bs = stock_data.get("fundamentals", {}).get("balance_sheet", {})
        inc = stock_data.get("fundamentals", {}).get("income_stmt", {})
        
        total_assets = extract_latest_yfinance_val(bs, "Total Assets")
        total_liabilities = extract_latest_yfinance_val(bs, "Total Liabilities Net Minority Interest")
        total_equity = extract_latest_yfinance_val(bs, "Stockholders Equity") or extract_latest_yfinance_val(bs, "Common Stock Equity")
        current_assets = extract_latest_yfinance_val(bs, "Current Assets")
        current_liabilities = extract_latest_yfinance_val(bs, "Current Liabilities")
        
        revenue = extract_latest_yfinance_val(inc, "Total Revenue")
        net_income = extract_latest_yfinance_val(inc, "Net Income")
        gross_profit = extract_latest_yfinance_val(inc, "Gross Profit")
    
    # Stock info
    info = stock_data.get("info", {})
    market_cap = info.get("marketCap", 0)
    beta = info.get("beta", 1.0)
    pe_ratio = info.get("trailingPE", 0)
    pb_ratio = info.get("priceToBook", 0)
    
    # Failsafe calculations
    if not current_assets and total_assets:
        current_assets = total_assets * 0.4 # rough proxy if missing
    if not current_liabilities and total_liabilities:
        current_liabilities = total_liabilities * 0.4
    if not total_equity and total_assets and total_liabilities:
        total_equity = total_assets - total_liabilities
        
    return {
        "balance_sheet": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "current_assets": current_assets,
            "current_liabilities": current_liabilities
        },
        "income_statement": {
            "revenue": revenue,
            "net_income": net_income,
            "gross_profit": gross_profit
        },
        "market_data": {
            "market_cap": market_cap,
            "beta": beta,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio
        }
    }
