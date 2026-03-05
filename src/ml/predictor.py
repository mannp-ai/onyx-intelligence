import joblib
import pandas as pd
import numpy as np
import os

class OnyxPredictor:
    def __init__(self):
        self.model = None
        self.classes = {
            0: "STRONG SELL",
            1: "SELL",
            2: "HOLD",
            3: "BUY",
            4: "STRONG BUY"
        }
        self._load_model()
        
    def _load_model(self):
        """Loads the pre-trained Random Forest model."""
        model_path = os.path.join(os.path.dirname(__file__), 'models/onyx_rf_model.pkl')
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Failed to load ML model: {e}")
        else:
            print(f"ML model not found at {model_path}. Please run src/ml/model.py.")

    def predict_verdict(self, ratios: dict, market_data: dict) -> tuple[str, int, dict]:
        """
        Takes live financial data, runs standard inferences, and predicts the verdict.
        Returns: (Verdict String, Extrapolated Score 0-100, Confidence Dictionary)
        """
        if self.model is None:
            return "UNKNOWN (MODEL ERROR)", 50, {}
            
        # Parse live data to match the 5 features the model was trained on
        try:
            liq = ratios.get("liquidity", {})
            lev = ratios.get("leverage", {})
            prof = ratios.get("profitability", {})
            val = ratios.get("valuation", {})
            
            # 1. Current Ratio
            current_ratio = liq.get("current_ratio", 1.0)
            # 2. Debt to Equity
            debt_to_equity = lev.get("debt_to_equity", 1.0)
            # 3. Net Margin
            net_margin = prof.get("net_margin", 0.0)
            # 4. P/E Ratio
            pe_ratio = val.get("pe_ratio", 15.0)
            # 5. Beta
            beta = market_data.get("beta", 1.0)
            
            # Construct DataFrame for the single sample
            # Must match columns: ['current_ratio', 'debt_to_equity', 'net_margin', 'pe_ratio', 'beta']
            X_live = pd.DataFrame([{
                'current_ratio': float(current_ratio),
                'debt_to_equity': float(debt_to_equity),
                'net_margin': float(net_margin),
                'pe_ratio': float(pe_ratio),
                'beta': float(beta)
            }])
            
            # 1. Predict Class
            pred_class = self.model.predict(X_live)[0]
            verdict = self.classes.get(pred_class, "HOLD")
            
            # 2. Predict Probabilities (Confidence)
            probs = self.model.predict_proba(X_live)[0]
            confidence = {self.classes[i]: round(float(p) * 100, 1) for i, p in enumerate(probs)}
            
            # 3. Reverse-engineer a final 0-100 score based on probabilities
            # (Class 0:0, Class 1:25, Class 2:50, Class 3:75, Class 4:100)
            expected_value = sum(p * (i * 25) for i, p in enumerate(probs))
            final_score = int(round(expected_value))
            
            return verdict, final_score, confidence
            
        except Exception as e:
            print(f"Inference error: {e}")
            return "ERROR", 50, {}

# Singleton instance
ml_predictor = OnyxPredictor()
