import os
import json
import logging
from database.connection import get_db_connection
from services.fraud_engine import analyze, _load_model

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'fraud_model.pkl')
META_PATH = os.path.join(BASE_DIR, 'models', 'model_metadata.json')

logger = logging.getLogger("mazi_logger")


def get_model_info() -> dict:
    """
    Retrieves model version, training metrics, ROC-AUC score, and feature attributes 
    to populate the system status panel on the dashboard.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
        return {
            "loaded": False,
            "message": "Model not trained. Execute: python core_ml/train_model.py"
        }
    
    try:
        with open(META_PATH, 'r', encoding='utf-8') as meta_file:
            meta = json.load(meta_file)
        
        return {
            "loaded": True,
            "version": meta.get('model_version', '1.0.0'),
            "roc_auc": float(meta.get('roc_auc', 0.0)),
            "training_samples": int(meta.get('training_samples', 0)),
            "features": meta.get('feature_names', [])
        }
    except Exception as exc:
        logger.error(f"Failed to parse model metadata JSON: {exc}")
        return {"loaded": False, "message": f"Metadata read error: {str(exc)}"}


def predict_transaction(transaction_data: dict) -> dict:
    """
    Executes the full prediction pipeline: runs ML feature inference, 
    evaluates threshold classification, and determines initial review status.
    """
    _load_model()
    
    risk_score = analyze(transaction_data)
    is_fraud = 1 if risk_score > 75 else 0
    status = 'Confirmed_Fraud' if risk_score > 85 else ('Flagged' if is_fraud else 'Safe')
    
    model_info = get_model_info()
    model_used = f"RandomForest_v{model_info.get('version', '1.0')}" if model_info['loaded'] else "heuristic_fallback"
    
    return {
        "is_fraud": bool(is_fraud),
        "risk_score": int(risk_score),
        "status": status,
        "model_used": model_used,
        "model_version": model_info.get('version', 'none')
    }


def store_prediction_result(transaction_id: str, result: dict):
    """
    Persists prediction metrics and model telemetry into the `fraud_predictions` SQLite table.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fraud_predictions (transaction_id, risk_score, is_fraud, model_version)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(transaction_id),
                int(result.get('risk_score', 0)),
                int(1 if result.get('is_fraud') else 0),
                str(result.get('model_used', 'unknown'))
            )
        )
        conn.commit()
        cursor.close()
    except Exception as exc:
        if conn:
            conn.rollback()
        logger.error(f"Database failure storing prediction result for {transaction_id}: {exc}")
    finally:
        if conn:
            conn.close()


def process_incoming_transaction(data: dict) -> dict:
    """
    Primary API gateway handler called by routes/api.py upon receiving live transactions.
    """
    evaluation_result = predict_transaction(data)
    return evaluation_result