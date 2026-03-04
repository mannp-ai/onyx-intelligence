def calculate_onyx_score(sub_scores: dict) -> int:
    """Aggregates sub-scores into final ONYX Score (0-100)."""
    scores = sub_scores.get("scores", {})
    
    # Weights based on typical value investing principles
    w_fh = 0.35  # Financial Health (Liquidity/Solvency)
    w_pr = 0.40  # Profitability
    w_va = 0.25  # Valuation
    
    base_score = (
        scores.get("financial_health", 50) * w_fh +
        scores.get("profitability", 50) * w_pr +
        scores.get("valuation", 50) * w_va
    )
    
    return int(min(max(base_score, 0), 100))

def determine_verdict(onyx_score: int, risk_score: int) -> str:
    """Applies PRD Decision Matrix to determine the final verdict."""
    if onyx_score <= 24 or risk_score >= 80:
        return "STRONG SELL"
    elif onyx_score >= 70 and risk_score < 40:
        return "STRONG BUY"
    elif onyx_score >= 55 and risk_score < 60:
        return "BUY"
    elif onyx_score >= 40:
        return "HOLD"
    else:
        return "SELL"

def generate_final_verdict(ratios: dict, sub_scores: dict) -> dict:
    """Combines score and logic into the final output object for the PDF/UI."""
    onyx_score = calculate_onyx_score(sub_scores)
    risk_score = sub_scores.get("scores", {}).get("risk", 50)
    verdict = determine_verdict(onyx_score, risk_score)
    
    # Simple sorting of factors
    factors = list(set(sub_scores.get("factors", [])))
    positive_signals = [f for f in factors if "High" in f or "Strong" in f or "Attractive" in f or "Low" in f]
    negative_signals = [f for f in factors if "Poor" in f or "Negative" in f or "Overvalued" in f or "Critically" in f]
    
    # Limit to top 3 as per PRD
    return {
        "onyx_score": onyx_score,
        "risk_score": risk_score,
        "verdict": verdict,
        "top_signals": positive_signals[:3] if positive_signals else ["Stable predictable metrics"],
        "risk_signals": negative_signals[:3] if negative_signals else ["Standard market risks apply"]
    }
