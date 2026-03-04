def calculate_ratios(normalized_data: dict) -> dict:
    """Computes core financial ratios from normalized data."""
    bs = normalized_data.get("balance_sheet", {})
    inc = normalized_data.get("income_statement", {})
    mkt = normalized_data.get("market_data", {})
    
    # Safely extract with defaults to avoid division by zero
    total_assets = bs.get("total_assets", 0)
    total_liabilities = bs.get("total_liabilities", 0)
    total_equity = bs.get("total_equity", 0)
    current_assets = bs.get("current_assets", 0)
    current_liabilities = bs.get("current_liabilities", 0)
    
    revenue = inc.get("revenue", 0)
    net_income = inc.get("net_income", 0)
    gross_profit = inc.get("gross_profit", 0)
    
    # Computations
    current_ratio = current_assets / current_liabilities if current_liabilities else 0
    debt_to_equity = total_liabilities / total_equity if total_equity else 0
    
    gross_margin = gross_profit / revenue if revenue else 0
    net_margin = net_income / revenue if revenue else 0
    roe = net_income / total_equity if total_equity else 0
    roa = net_income / total_assets if total_assets else 0
    
    return {
        "liquidity": {
            "current_ratio": round(current_ratio, 2)
        },
        "leverage": {
            "debt_to_equity": round(debt_to_equity, 2)
        },
        "profitability": {
            "gross_margin": round(gross_margin, 4),
            "net_margin": round(net_margin, 4),
            "roe": round(roe, 4),
            "roa": round(roa, 4)
        },
        "valuation": {
            "pe_ratio": round(mkt.get("pe_ratio", 0), 2),
            "pb_ratio": round(mkt.get("pb_ratio", 0), 2)
        },
        "risk": {
            "beta": round(mkt.get("beta", 1.0), 2)
        }
    }
