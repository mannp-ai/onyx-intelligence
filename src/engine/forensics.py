def calculate_dcf(free_cash_flow: float, shares_outstanding: float, beta: float, current_price: float) -> dict:
    """Computes a 5-Year DCF Model to find Intrinsic Share Price."""
    if free_cash_flow <= 0 or shares_outstanding <= 0:
        return {"target_price": 0.0, "upside": 0.0, "is_valid": False}
        
    # Assumptions
    growth_rate = 0.05 # 5% assumed growth
    terminal_growth_rate = 0.02 # 2% terminal growth
    
    # Discount Rate (WACC proxy using CAPM)
    risk_free_rate = 0.04
    market_return = 0.10
    discount_rate = risk_free_rate + beta * (market_return - risk_free_rate)
    
    # Cap discount rate to reasonable bounds
    discount_rate = max(0.05, min(0.20, discount_rate))
    
    # Project FCF for 5 years
    future_fcf = []
    current_fcf = free_cash_flow
    for _ in range(5):
        current_fcf *= (1 + growth_rate)
        future_fcf.append(current_fcf)
        
    # Calculate Terminal Value
    terminal_value = (future_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    
    # Discount to Present Value
    pv_fcf = sum(fcf / ((1 + discount_rate) ** i) for i, fcf in enumerate(future_fcf, 1))
    pv_tv = terminal_value / ((1 + discount_rate) ** 5)
    
    intrinsic_value = pv_fcf + pv_tv
    target_price = intrinsic_value / shares_outstanding
    
    upside = ((target_price - current_price) / current_price) if current_price else 0.0
    
    return {
        "target_price": round(target_price, 2),
        "upside": round(upside, 4),
        "is_valid": True
    }

def calculate_piotroski(normalized_data: dict) -> int:
    """Calculates the Piotroski F-Score (0-9) reflecting accounting strength."""
    score = 0
    bs = normalized_data.get("balance_sheet", {})
    inc = normalized_data.get("income_statement", {})
    cf = normalized_data.get("cash_flow", {})
    
    roa = inc.get("net_income", 0) / bs.get("total_assets", 1) if bs.get("total_assets", 0) else 0
    cfo = cf.get("operating_cash_flow", 0)
    
    # 1. Positive ROA
    if roa > 0: score += 1
    # 2. Positive CFO
    if cfo > 0: score += 1
    # 3. CFO > Net Income
    if cfo > inc.get("net_income", 0): score += 1
    # 4. Long term debt logic (proxy: current assets > current liab)
    if bs.get("current_assets", 0) > bs.get("current_liabilities", 0): score += 2
    # 5. Gross margin > 0
    if inc.get("gross_profit", 0) > 0: score += 2
    # 6. Asset Turnover > 0.5
    asset_turnover = inc.get("revenue", 0) / bs.get("total_assets", 1) if bs.get("total_assets", 0) else 0
    if asset_turnover > 0.5: score += 2
    
    return min(9, score)

def calculate_altman(normalized_data: dict, market_cap: float) -> dict:
    """Calculates the Altman Z-Score predicting bankruptcy risk."""
    bs = normalized_data.get("balance_sheet", {})
    inc = normalized_data.get("income_statement", {})
    
    total_assets = bs.get("total_assets", 0)
    if not total_assets:
        return {"score": 0.0, "risk_zone": "Unknown"}
        
    A = (bs.get("current_assets", 0) - bs.get("current_liabilities", 0)) / total_assets
    B = bs.get("retained_earnings", 0) / total_assets
    C = inc.get("ebit", 0) / total_assets
    total_liab = bs.get("total_liabilities", 0)
    D = market_cap / total_liab if total_liab else 0
    E = inc.get("revenue", 0) / total_assets
    
    z_score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
    
    if z_score > 2.99:
        zone = "Safe"
    elif z_score > 1.81:
        zone = "Grey"
    else:
        zone = "Distress"
        
    return {
        "score": round(z_score, 2),
        "risk_zone": zone
    }

def generate_forensics(normalized_data: dict) -> dict:
    """Orchestrates the calculation of all forensic indicators."""
    cf = normalized_data.get("cash_flow", {})
    mkt = normalized_data.get("market_data", {})
    
    fcf = cf.get("free_cash_flow", 0)
    shares = mkt.get("shares_outstanding", 0)
    beta = mkt.get("beta", 1.0)
    price = mkt.get("current_price", 0)
    market_cap = mkt.get("market_cap", 0)
    
    dcf = calculate_dcf(fcf, shares, beta, price)
    f_score = calculate_piotroski(normalized_data)
    z_score = calculate_altman(normalized_data, market_cap)
    
    return {
        "dcf": dcf,
        "piotroski_f_score": f_score,
        "altman_z_score": z_score
    }
