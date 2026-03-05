import pandas as pd
import numpy as np
import os
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(num_samples=10000):
    """
    Generates a synthetic financial dataset mimicking historical companies.
    Features: current_ratio, debt_to_equity, net_margin, pe_ratio, beta
    Target: Verdict (0: Strong Sell, 1: Sell, 2: Hold, 3: Buy, 4: Strong Buy)
    """
    print(f"Generating {num_samples} synthetic financial records...")
    
    # Generate realistic financial feature distributions
    # Current Ratio: normally around 1.5, bounded at >0
    current_ratio = np.random.normal(loc=1.5, scale=0.8, size=num_samples)
    current_ratio = np.clip(current_ratio, 0.1, 8.0)
    
    # Debt to Equity: normally around 1.0, bounded
    debt_to_equity = np.random.normal(loc=1.2, scale=1.0, size=num_samples)
    debt_to_equity = np.clip(debt_to_equity, 0.0, 10.0)
    
    # Net Margin: -50% to +50%
    net_margin = np.random.normal(loc=0.08, scale=0.15, size=num_samples)
    net_margin = np.clip(net_margin, -0.60, 0.60)
    
    # P/E Ratio: 5 to 100, occasionally negative (unprofitable)
    pe_ratio = np.random.normal(loc=25, scale=20, size=num_samples)
    pe_ratio = np.where(net_margin < 0, np.random.uniform(-50, -1, size=num_samples), pe_ratio)
    pe_ratio = np.clip(pe_ratio, -100, 200)
    
    # Beta: 0.5 to 2.5
    beta = np.random.normal(loc=1.1, scale=0.4, size=num_samples)
    beta = np.clip(beta, 0.1, 4.0)

    # DataFrame construction
    df = pd.DataFrame({
        'current_ratio': current_ratio,
        'debt_to_equity': debt_to_equity,
        'net_margin': net_margin,
        'pe_ratio': pe_ratio,
        'beta': beta
    })
    
    # Deterministic mapping logic to approximate ground truth labels
    # We create a hidden "score" (0-100) and map to 0-4 classes.
    # This simulates historical market behavior where these metrics dictate stock success.
    
    scores = np.ones(num_samples) * 50
    
    # Health bonuses/penalties
    scores += np.where(df['current_ratio'] > 2.0, 15, 0)
    scores -= np.where(df['current_ratio'] < 1.0, 15, 0)
    scores -= np.where(df['debt_to_equity'] > 2.5, 20, 0)
    scores += np.where(df['debt_to_equity'] < 0.5, 10, 0)
    
    # Profitability bonuses/penalties
    scores += np.where(df['net_margin'] > 0.15, 20, 0)
    scores -= np.where(df['net_margin'] < 0, 25, 0)
    
    # Valuation
    scores += np.where((df['pe_ratio'] > 0) & (df['pe_ratio'] < 15), 15, 0)
    scores -= np.where(df['pe_ratio'] > 40, 15, 0)
    
    # Risk
    scores -= np.where(df['beta'] > 1.5, 10, 0)
    scores += np.where(df['beta'] < 0.8, 10, 0)
    
    # Add slight random noise to prevent the model from just perfectly learning an IF/ELSE tree
    noise = np.random.normal(0, 5, num_samples)
    scores = np.clip(scores + noise, 0, 100)
    
    # Map raw score to 5 classes
    def map_verdict(score):
        if score >= 85: return 4 # Strong Buy
        elif score >= 65: return 3 # Buy
        elif score >= 40: return 2 # Hold
        elif score >= 20: return 1 # Sell
        else: return 0 # Strong Sell

    df['verdict'] = np.vectorize(map_verdict)(scores)
    
    # Save the synthetic dataset
    os.makedirs('src/data/cache', exist_ok=True)
    out_path = 'src/data/cache/synthetic_training_data.csv'
    df.to_csv(out_path, index=False)
    print(f"Dataset generated successfully -> {out_path}")
    
    return df

if __name__ == "__main__":
    generate_synthetic_data()
