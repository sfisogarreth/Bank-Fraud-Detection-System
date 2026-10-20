import time
import logging
from flask import Blueprint, request, jsonify
from database.connection import get_db_connection
from services.prediction_service import process_incoming_transaction

api_bp = Blueprint('api', __name__)
logger = logging.getLogger("mazi_logger")


@api_bp.route('/v1/transactions', methods=['POST'])
def receive_transaction():
    data = request.get_json()

    # Validation
    required_fields = ['account_number', 'amount', 'location', 'type', 'oldbalanceOrg', 'newbalanceOrig']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing transaction attributes"}), 400

    # Safe type conversion
    try:
        amount = float(data['amount'])
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid amount format"}), 400

    account = str(data['account_number'])
    location = str(data['location'])
    
    # 🔥 REAL ML PREDICTION
    result = process_incoming_transaction(data)
    risk_score = result['risk_score']
    is_fraud = 1 if risk_score > 75 else 0
    status = result['status']
    transaction_id = f"TXN{int(time.time() * 1000)}"

    # Save to SQLite
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions 
            (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type,
             oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id, account, amount, location, risk_score, status, is_fraud,
            data.get('type', 'PAYMENT'),
            float(data.get('oldbalanceOrg', 0)),
            float(data.get('newbalanceOrig', 0)),
            float(data.get('oldbalanceDest', 0)),
            float(data.get('newbalanceDest', 0))
        ))
        
        conn.commit()
        cursor.close()

        if is_fraud:
            logger.warning(f"HIGH RISK: {transaction_id} | Account {account} | Amount ${amount} | Score {risk_score} | Model: {result['model_used']}")

        return jsonify({
            "status": "success",
            "transaction_id": transaction_id,
            "risk_score": risk_score,
            "decision": status,
            "model_used": result['model_used'],
            "model_version": result.get('model_version', 'unknown')
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to process transaction: {e}")
        return jsonify({"status": "error", "message": f"Database failure: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@api_bp.route('/v1/model/status', methods=['GET'])
def model_status():
    """Check if ML model is loaded and ready."""
    from services.prediction_service import get_model_info
    info = get_model_info()
    return jsonify({
        "status": "ready" if info['loaded'] else "not_trained",
        "details": info
    }), 200