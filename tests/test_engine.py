import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.engine.ratios import calculate_ratios
from src.engine.scorer import generate_sub_scores
from src.engine.aggregator import calculate_onyx_score, determine_verdict

def test_ratio_calculator():
    m_data = {
        "balance_sheet": {"current_assets": 200, "current_liabilities": 100, "total_assets": 1000, "total_liabilities": 500, "total_equity": 500},
        "income_statement": {"revenue": 1000, "net_income": 200, "gross_profit": 500},
        "market_data": {"pe_ratio": 15, "pb_ratio": 1.5, "beta": 1.2}
    }
    
    ratios = calculate_ratios(m_data)
    assert ratios["liquidity"]["current_ratio"] == 2.0
    assert ratios["leverage"]["debt_to_equity"] == 1.0
    assert ratios["profitability"]["net_margin"] == 0.2
    assert ratios["profitability"]["roe"] == 0.4

def test_scoring_logic():
    ratios = {
        "liquidity": {"current_ratio": 2.5},
        "leverage": {"debt_to_equity": 0.5},
        "profitability": {"net_margin": 0.20, "roe": 0.25},
        "valuation": {"pe_ratio": 12, "pb_ratio": 1.5},
        "risk": {"beta": 1.0}
    }
    
    sub = generate_sub_scores(ratios)
    fh = sub["scores"]["financial_health"]
    pr = sub["scores"]["profitability"]
    va = sub["scores"]["valuation"]
    ri = sub["scores"]["risk"]
    
    # Very strong metrics
    assert fh > 80
    assert pr > 80
    assert va > 80
    assert ri < 40 
    
    onyx = calculate_onyx_score(sub)
    assert onyx > 80 # Should be high
    assert determine_verdict(onyx, ri) == "STRONG BUY"
