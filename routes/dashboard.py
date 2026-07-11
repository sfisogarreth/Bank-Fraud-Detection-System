from flask import Blueprint, render_template, jsonify
from services.transaction_service import get_transaction_stats, get_recent_transactions, get_recent_cases

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    stats = get_transaction_stats()
    recent = get_recent_transactions(10)
    cases = get_recent_cases(5)

    # Format cases for the template (add type and loss fields)
    fraud_cases = []
    for case in cases:
        fraud_cases.append({
            'id': case['id'],
            'risk_score': case['risk_score'],
            'type': 'Account Takeover' if case['risk_score'] > 90 else 'Card Fraud' if case['risk_score'] > 80 else 'Suspicious Activity',
            'loss': f"{case['amount']:,.2f}"
        })

    # XAI features for the latest case
    latest_case = {
        'id': fraud_cases[0]['id'] if fraud_cases else 'N/A',
        'xai_features': [
            {'name': 'Transaction Velocity', 'weight': 85},
            {'name': 'Amount Anomaly', 'weight': 72},
            {'name': 'Location Risk', 'weight': 45},
            {'name': 'Time Pattern', 'weight': 38}
        ]
    }

    return render_template("dashboard.html", stats=stats, transactions=recent, 
                         fraud_cases=fraud_cases, latest_case=latest_case)

@dashboard_bp.route('/api/stats')
def api_stats():
    """JSON endpoint for AJAX updates (live dashboard)."""
    return jsonify(get_transaction_stats())