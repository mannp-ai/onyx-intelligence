def score_financial_health(ratios: dict) -> tuple[int, list]:
    """Evaluates balance sheet strength. Returns (score 0-100, [factors])."""
    score = 50
    factors = []
    
    liq = ratios.get("liquidity", {})
    lev = ratios.get("leverage", {})
    
    cr = liq.get("current_ratio", 0)
    dte = lev.get("debt_to_equity", 0)
    
    if cr >= 2.0:
        score += 25
        factors.append("Strong liquidity (Current Ratio >= 2.0)")
    elif cr >= 1.0:
        score += 10
        factors.append("Adequate liquidity (Current Ratio >= 1.0)")
    else:
        score -= 20
        factors.append("Poor liquidity (Current Ratio < 1.0)")
        
    if dte == 0:
        pass # Handle Missing
    elif dte < 1.0:
        score += 25
        factors.append("Low debt burden (D/E < 1.0)")
    elif dte > 2.5:
        score -= 25
        factors.append("High debt burden (D/E > 2.5)")
        
    return min(max(score, 0), 100), factors

def score_profitability(ratios: dict) -> tuple[int, list]:
    score = 50
    factors = []
    
    prof = ratios.get("profitability", {})
    nm = prof.get("net_margin", 0)
    roe = prof.get("roe", 0)
    
    if nm > 0.15:
        score += 25
        factors.append("High net profit margin (>15%)")
    elif nm < 0:
        score -= 30
        factors.append("Negative net profit margin")
        
    if roe > 0.15:
        score += 25
        factors.append("Strong Return on Equity (>15%)")
        
    return min(max(score, 0), 100), factors

def score_valuation(ratios: dict) -> tuple[int, list]:
    score = 50
    factors = []
    
    val = ratios.get("valuation", {})
    pe = val.get("pe_ratio", 0)
    pb = val.get("pb_ratio", 0)
    
    if pe > 0 and pe < 15:
        score += 30
        factors.append("Attractive P/E valuation (<15x)")
    elif pe > 40:
        score -= 25
        factors.append("Overvalued P/E ratio (>40x)")
        
    if pb > 0 and pb < 2.0:
        score += 20
        factors.append("Low Price-to-Book ratio (<2.0x)")
        
    return min(max(score, 0), 100), factors

def score_risk(ratios: dict) -> tuple[int, list]:
    # Higher risk score means HIGHER risk (bad). Max 100.
    risk = 20
    factors = []
    
    beta = ratios.get("risk", {}).get("beta", 1.0)
    dte = ratios.get("leverage", {}).get("debt_to_equity", 0)
    
    if beta > 1.5:
        risk += 30
        factors.append("High market volatility (Beta > 1.5)")
        
    if dte > 3.0:
        risk += 30
        factors.append("Critically high leverage risk")
        
    return min(risk, 100), factors
    
def generate_sub_scores(ratios: dict) -> dict:
    """Combines all scoring logic into a unified profile."""
    fh, fh_f = score_financial_health(ratios)
    pr, pr_f = score_profitability(ratios)
    va, va_f = score_valuation(ratios)
    ri, ri_f = score_risk(ratios)
    
    return {
        "scores": {
            "financial_health": fh,
            "profitability": pr,
            "valuation": va,
            "risk": ri
        },
        "factors": fh_f + pr_f + va_f + ri_f
    }
