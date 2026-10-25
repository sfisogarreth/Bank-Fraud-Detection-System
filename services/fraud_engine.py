import os
import json
import joblib
import numpy as np
import logging

# Establish absolute paths anchored to project root structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
META_PATH = os.path.join(BASE_DIR, "models", "model_metadata.json")

logger = logging.getLogger("mazi_logger")

# Module-level caching for singleton model state
_model_instance = None
_model_metadata = None


def _load_model():
    """
    Safely lazy-loads the trained Random Forest classifier and feature metadata 
    from disk into memory once, preventing redundant file I/O overhead.
    """
    global _model_instance, _model_metadata
    
    if _model_instance is not None:
        return _model_instance, _model_metadata
    
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"CRITICAL: ML model binary missing at {MODEL_PATH}. Run core_ml/train_model.py.")
        return None, None
    
    if not os.path.exists(META_PATH):
        logger.warning(f"CRITICAL: Model metadata missing at {META_PATH}. Retrain the model pipeline.")
        return None, None
    
    try:
        _model_instance = joblib.load(MODEL_PATH)
        with open(META_PATH, 'r', encoding='utf-8') as meta_file:
            _model_metadata = json.load(meta_file)
        
        logger.info(
            f"Successfully loaded ML model v{_model_metadata.get('model_version', '1.0.0')} "
            f"(Holdout ROC-AUC: {_model_metadata.get('roc_auc', 0.0):.4f})"
        )
    except Exception as exc:
        logger.error(f"Failed to load machine learning assets from disk: {exc}")
        _model_instance, _model_metadata = None, None
        
    return _model_instance, _model_metadata


def analyze(transaction_data: dict) -> int:
    """
    Analyzes an incoming transaction payload against the Random Forest classifier.
    Performs feature alignment, robust one-hot encoding normalization, 
    and returns a standardized integer risk score from 0 to 100.
    """
    model, metadata = _load_model()
    
    # Fallback heuristic calculation if model binaries are uninitialized
    if model is None or metadata is None:
        logger.warning("Executing heuristic fallback scoring due to unavailable ML model.")
        amount = float(transaction_data.get('amount', 0.0))
        old_bal = float(transaction_data.get('oldbalanceOrg', 0.0))
        drain_factor = (amount / (old_bal + 1.0)) * 50.0
        return min(100, max(0, int((amount / 1000.0) * 1.5 + drain_factor)))

    try:
        features = {}
        
        # 1. Map core numeric transaction attributes safely with default bounds
        features['step'] = float(transaction_data.get('step', 1.0))
        features['amount'] = float(transaction_data.get('amount', 0.0))
        features['oldbalanceOrg'] = float(transaction_data.get('oldbalanceOrg', 0.0))
        features['newbalanceOrig'] = float(transaction_data.get('newbalanceOrig', 0.0))
        features['oldbalanceDest'] = float(transaction_data.get('oldbalanceDest', 0.0))
        features['newbalanceDest'] = float(transaction_data.get('newbalanceDest', 0.0))
        
        # 2. Normalize transaction type string to uppercase to match training columns exactly
        raw_type = transaction_data.get('type', 'PAYMENT')
        t_type = str(raw_type).strip().upper()
        
        # 3. Process categorical one-hot encoding columns defined in model metadata
        for type_col in metadata.get('type_columns', []):
            type_name = type_col.replace('type_', '')
            features[type_col] = 1 if t_type == type_name else 0
        
        # 4. Construct feature vector matching the exact training column order
        feature_vector = [features.get(feature_name, 0.0) for feature_name in metadata['feature_names']]
        X = np.array([feature_vector], dtype=np.float64)
        
        # 5. Execute model inference probability calculation
        probabilities = model.predict_proba(X)
        fraud_probability = float(probabilities[0][1])
        risk_score = int(round(fraud_probability * 100.0))
        
        return min(100, max(0, risk_score))

    except Exception as exc:
        logger.error(f"Runtime execution error during ML transaction analysis: {exc}")
        # Safe fallback default risk score on runtime exception
        return 50


if __name__ == '__main__':
    # Local diagnostic verification block
    sample_payload = {
        'step': 1,
        'amount': 75000.0,
        'oldbalanceOrg': 75000.0,
        'newbalanceOrig': 0.0,
        'oldbalanceDest': 100.0,
        'newbalanceDest': 75100.0,
        'type': 'TRANSFER'
    }
    print(f"Diagnostic Test Inference Risk Score: {analyze(sample_payload)}")