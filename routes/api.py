import time
import logging
from flask import Blueprint, request, jsonify
from app import csrf
from database.connection import get_db_connection
from services.prediction_service import process_incoming_transaction, store_prediction_result, get_model_info
from services.risk_service import calculate_risk_score
from init_db import ensure_schema_upgrades

api_bp = Blueprint('api', __name__)
logger = logging.getLogger("mazi_logger")

# Ensure existing mazi.db has the explanation column and indexes on startup
ensure_schema_upgrades()


@api_bp.route('/v1/transactions', methods=['POST'])
@csrf.exempt
def receive_transaction():
    data = request.get_json(silent=True)

    required_fields = ['account_number', 'amount', 'location', 'type', 'oldbalanceOrg', 'newbalanceOrig']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing transaction attributes"}), 400

    try:
        amount = float(data['amount'])
        old_bal = float(data.get('oldbalanceOrg', 0))
        new_bal = float(data.get('newbalanceOrig', max(0.0, old_bal - amount)))
        if new_bal == 0.0 and old_bal > amount:
            new_bal = round(old_bal - amount, 2)
        data['newbalanceOrig'] = new_bal
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid numeric format"}), 400

    account = str(data['account_number'])
    location = str(data['location'])
    tx_type = str(data.get('type', 'PAYMENT')).strip().upper()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Check recent account velocity in SQLite for C++ fast_math engine
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM transactions WHERE account_number = ?",
            (account,)
        )
        tx_velocity = int(cursor.fetchone()["cnt"] or 0) + 1

        # 2. ML Model Prediction
        ml_result = process_incoming_transaction(data)
        ml_score = float(ml_result['risk_score'])

        # 3. C++ fast_math Velocity Risk Calculation
        cpp_score = float(calculate_risk_score(amount, tx_velocity))

        # 4. Hybrid Score (65% ML + 35% C++ Velocity + Geolocation Proxy check)
        proxy_boost = 15.0 if ("Proxy" in location or "Lagos" in location) else 0.0
        combined_score = int(min(99, max(4, round((ml_score * 0.65) + (cpp_score * 0.35) + proxy_boost))))

        # 5. Respect dynamic fraud threshold from settings table
        cursor.execute("SELECT fraud_threshold FROM settings WHERE id = 1")
        setting_row = cursor.fetchone()
        threshold = int(setting_row["fraud_threshold"]) if setting_row and setting_row["fraud_threshold"] else 75

        is_fraud = 1 if combined_score >= threshold else 0
        status = 'Flagged' if is_fraud else ('Reviewing' if combined_score >= 50 else 'Safe')
        transaction_id = f"TXN{int(time.time() * 1000)}"

        # 6. Build Dynamic Explainable AI (XAI) Reason String for this specific transaction
        drain_pct = round((amount / (old_bal + 1.0)) * 100.0, 1) if old_bal > 0 else 100.0
        reasons = []
        if amount >= 15000:
            reasons.append(f"High-value {tx_type} of R{amount:,.2f}")
        else:
            reasons.append(f"{tx_type} of R{amount:,.2f}")

        if drain_pct >= 70.0:
            reasons.append(f"High account balance depletion ({drain_pct}% drained)")
        if proxy_boost > 0:
            reasons.append(f"High-risk proxy/foreign geolocation ({location})")
        if tx_velocity > 2:
            reasons.append(f"Elevated account velocity ({tx_velocity} transactions recorded)")

        reasons.append(f"Hybrid Engine Breakdown -> Random Forest ML: {int(ml_score)}%, C++ Velocity Engine: {int(cpp_score)}%")
        explanation_text = " | ".join(reasons)

        cursor.execute("""
            INSERT INTO transactions 
            (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type,
             oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id, account, amount, location, combined_score, status, is_fraud,
            tx_type,
            old_bal,
            new_bal,
            float(data.get('oldbalanceDest', 0)),
            float(data.get('newbalanceDest', amount)),
            explanation_text
        ))

        conn.commit()
        cursor.close()

        # Store in fraud_predictions log table
        ml_result['risk_score'] = combined_score
        ml_result['is_fraud'] = bool(is_fraud)
        store_prediction_result(transaction_id, ml_result)

        if is_fraud:
            logger.warning(
                f"HIGH RISK: {transaction_id} | Account {account} | Amount R{amount:,.2f} | Score {combined_score}% | Model: {ml_result['model_used']}"
            )

        return jsonify({
            "status": "success",
            "transaction_id": transaction_id,
            "risk_score": combined_score,
            "decision": status,
            "explanation": explanation_text,
            "model_used": ml_result['model_used'],
            "model_version": ml_result.get('model_version', '1.0.0')
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
    info = get_model_info()
    return jsonify({
        "status": "ready" if info['loaded'] else "not_trained",
        "details": info
    }), 200