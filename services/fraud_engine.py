import os
import json
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
META_PATH = os.path.join(BASE_DIR, "models", "model_metadata.json")

model = None
metadata = None


def _load_model():
    """Lazy-load model and metadata once."""
    global model, metadata
    
    if model is not None:
        return
    
    if not os.path.exists(MODEL_PATH):
        print("⚠️ No trained model found. Run: python core_ml/train_model.py")
        return
    
    if not os.path.exists(META_PATH):
        print("⚠️ No model metadata found. Retrain with the new train_model.py")
        return
    
    model = joblib.load(MODEL_PATH)
    
    with open(META_PATH, 'r') as f:
        metadata = json.load(f)
    
    print(f"✅ Model v{metadata.get('model_version', '?')} loaded (ROC-AUC: {metadata.get('roc_auc', 'N/A')})")


def analyze(transaction_data):
    """
    Analyze a transaction using the trained Random Forest model.
    Returns risk score 0-100.
    """
    _load_model()
    
    if model is None or metadata is None:
        # Fallback: simple heuristic if model missing
        amount = float(transaction_data.get('amount', 0))
        risk = min(100, int(amount / 500))
        return risk

    try:
        # Build feature dict with exact names model expects
        features = {}
        
        # Numeric features
        features['step'] = float(transaction_data.get('step', 1))
        features['amount'] = float(transaction_data.get('amount', 0))
        features['oldbalanceOrg'] = float(transaction_data.get('oldbalanceOrg', 0))
        features['newbalanceOrig'] = float(transaction_data.get('newbalanceOrig', 0))
        features['oldbalanceDest'] = float(transaction_data.get('oldbalanceDest', 0))
        features['newbalanceDest'] = float(transaction_data.get('newbalanceDest', 0))
        
        # One-Hot Encoding matching training (drop_first=True)
        t_type = transaction_data.get('type', 'PAYMENT')
        ref_cat = metadata.get('reference_category', 'CASH_IN')
        
        for type_col in metadata.get('type_columns', []):
            # type_col looks like "type_CASH_OUT"
            type_name = type_col.replace('type_', '')
            features[type_col] = 1 if t_type == type_name else 0
        
        # Build array in EXACT feature order
        feature_vector = [features.get(name, 0) for name in metadata['feature_names']]
        X = np.array([feature_vector])
        
        # Predict
        probability = model.predict_proba(X)[0][1]
        risk_score = int(probability * 100)
        
        return risk_score

    except Exception as e:
        print(f"⚠️ ML Analysis Error: {e}")
        # Safe fallback
        return 50


if __name__ == '__main__':
    # Quick test
    test_txn = {
        'step': 1,
        'amount': 50000,
        'oldbalanceOrg': 50000,
        'newbalanceOrig': 0,
        'oldbalanceDest': 0,
        'newbalanceDest': 50000,
        'type': 'TRANSFER'
    }
    print(f"Test risk score: {analyze(test_txn)}")