import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    """Trains a Random Forest Classifier on the synthetic financial dataset."""
    data_path = 'src/data/cache/synthetic_training_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: Training data not found at {data_path}. Run dataset_generator.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Features (X) and Target (y)
    X = df[['current_ratio', 'debt_to_equity', 'net_margin', 'pe_ratio', 'beta']]
    y = df['verdict']
    
    # Train/Test Split (80% training, 20% evaluation)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training RandomForestClassifier on {len(X_train)} samples...")
    # Initialize the model
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    
    # Train!
    clf.fit(X_train, y_train)
    
    # Evaluate
    print("Evaluating model on test data...")
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {acc * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Strong Sell', 'Sell', 'Hold', 'Buy', 'Strong Buy']))
    
    # Save the model
    os.makedirs('src/ml/models', exist_ok=True)
    model_path = 'src/ml/models/onyx_rf_model.pkl'
    joblib.dump(clf, model_path)
    print(f"\nModel saved successfully to {model_path}!")

if __name__ == "__main__":
    train_model()
