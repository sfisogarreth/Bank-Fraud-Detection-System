import joblib
import os
import numpy as np
from services.transaction_service import get_db_connection

MODEL_PATH = os.path.join('models', 'fraud_model.pkl')

# Load model once at startup
_model = None

def get_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
            print("✅ Fraud model loaded")
        else:
            print("⚠️ No model found at", MODEL_PATH)
    return _model

def predict_transaction(amount, account_history=None):
    """
    Simple rule-based fallback if model isn't trained yet.
    Replace with actual model.predict() once your notebook exports properly.
    """
    model = get_model()
    
    if model is None:
        # Fallback: heuristic scoring for demo purposes
        risk = min(100, int(amount / 250))
        is_fraud = risk > 60
        return {
            "is_fraud": is_fraud,
            "risk_score": risk,
            "status": "Flagged" if is_fraud else "Safe",
            "model_used": "heuristic_fallback"
        }
    
    # When your model is ready, use this:
    # features = np.array([[amount, ...]])  # Match your training features
    # prediction = model.predict(features)[0]
    # probability = model.predict_proba(features)[0][1]
    # return {
    #     "is_fraud": bool(prediction),
    #     "risk_score": int(probability * 100),
    #     "status": "Flagged" if prediction else "Safe",
    #     "model_used": "fraud_model_v1"
    # }
    
    return {"error": "Model integration pending"}

def store_prediction_result(transaction_id, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fraud_predictions (transaction_id, risk_score, is_fraud, model_version)
        VALUES (?, ?, ?, ?)
    """, (transaction_id, result['risk_score'], int(result['is_fraud']), result.get('model_used', 'unknown')))
    conn.commit()
    conn.close()