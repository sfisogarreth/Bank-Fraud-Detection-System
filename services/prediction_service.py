import os
import json
import joblib
import numpy as np
from database.connection import get_db_connection
from services.fraud_engine import analyze, _load_model

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'fraud_model.pkl')
META_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_metadata.json')


def get_model_info():
    """Return model status and metadata."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
        return {
            "loaded": False,
            "message": "Model not trained. Run: python core_ml/train_model.py"
        }
    
    with open(META_PATH, 'r') as f:
        meta = json.load(f)
    
    return {
        "loaded": True,
        "version": meta.get('model_version'),
        "roc_auc": meta.get('roc_auc'),
        "training_samples": meta.get('training_samples'),
        "features": meta.get('feature_names', [])
    }


def predict_transaction(transaction_data):
    """
    Full prediction pipeline: ML score + status + logging.
    """
    _load_model()
    
    risk_score = analyze(transaction_data)
    is_fraud = 1 if risk_score > 75 else 0
    status = 'Flagged' if is_fraud else 'Safe'
    
    # Check if model is actually being used or fallback
    model_info = get_model_info()
    model_used = "fraud_model_v1" if model_info['loaded'] else "heuristic_fallback"
    
    return {
        "is_fraud": bool(is_fraud),
        "risk_score": risk_score,
        "status": status,
        "model_used": model_used,
        "model_version": model_info.get('version', 'none')
    }


def store_prediction_result(transaction_id, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fraud_predictions (transaction_id, risk_score, is_fraud, model_version)
        VALUES (?, ?, ?, ?)
    """, (transaction_id, result['risk_score'], int(result['is_fraud']), result.get('model_used', 'unknown')))
    conn.commit()
    conn.close()


# API endpoint helper
def process_incoming_transaction(data):
    """
    Called by routes/api.py when a transaction arrives.
    Returns the full result dict.
    """
    result = predict_transaction(data)
    return result