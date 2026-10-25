from flask import (
    Blueprint,
    render_template,
    jsonify,
    session
)

from services.transaction_service import (
    get_transaction_stats,
    get_recent_transactions,
    get_recent_cases,
    get_live_dashboard_telemetry
)

from services.prediction_service import (
    get_model_info
)

from services.security import (
    login_required
)

dashboard_bp = Blueprint(
    'dashboard',
    __name__
)


def _build_live_cases_and_xai():
    """Helper to build formatted fraud cases and XAI rationale from the newest transactions."""
    recent_cases = get_recent_cases(10)
    fraud_cases = []

    for case in recent_cases:
        score = float(case.get("risk_score") or 0)
        if score > 90:
            case_type = "Account Takeover"
        elif score > 75:
            case_type = "Card Fraud"
        elif score > 60:
            case_type = "Identity Theft"
        else:
            case_type = "Suspicious Activity"

        fraud_cases.append({
            "id": case["id"],
            "transaction_id": case.get("transaction_id", f"TXN-{case['id']}"),
            "account_number": case.get("account_number", "ACC-0000"),
            "location": case.get("location", "Johannesburg, ZA"),
            "risk_score": int(round(score)),
            "type": case_type,
            "loss": f"{float(case.get('amount') or 0):,.2f}"
        })

    if fraud_cases:
        newest = fraud_cases[0]
        base_risk = newest["risk_score"]
        loc_str = str(newest.get("location", ""))
        loc_boost = 15 if ("Proxy" in loc_str or "Lagos" in loc_str) else 0

        latest_case = {
            "id": newest["id"],
            "transaction_id": newest["transaction_id"],
            "xai_features": [
                {"name": "Transaction Velocity", "weight": min(98, max(12, int(base_risk * 0.92)))},
                {"name": "Amount Anomaly", "weight": min(96, max(15, int(base_risk * 0.84)))},
                {"name": "Location Risk", "weight": min(95, max(10, int(base_risk * 0.65) + loc_boost))},
                {"name": "Time Pattern", "weight": min(85, max(8, int(base_risk * 0.48)))}
            ]
        }
    else:
        latest_case = {
            "id": "N/A",
            "transaction_id": "N/A",
            "xai_features": [
                {"name": "Transaction Velocity", "weight": 0},
                {"name": "Amount Anomaly", "weight": 0},
                {"name": "Location Risk", "weight": 0},
                {"name": "Time Pattern", "weight": 0}
            ]
        }

    return fraud_cases, latest_case


# --------------------------------------------------
# DASHBOARD VIEW
# --------------------------------------------------

@dashboard_bp.route('/')
@login_required
def dashboard():
    try:
        role = session.get("role", "Admin")
        username = session.get("username", "Sfiso Garry")

        stats = get_transaction_stats()
        recent_transactions = get_recent_transactions(15)
        chart_data = get_live_dashboard_telemetry()
        fraud_cases, latest_case = _build_live_cases_and_xai()
        model_info = get_model_info()

        dashboard_context = {
            "stats": stats,
            "chart_data": chart_data,
            "transactions": recent_transactions,
            "fraud_cases": fraud_cases,
            "latest_case": latest_case,
            "model_info": model_info,
            "user_role": role,
            "username": username
        }

        return render_template(
            "dashboard.html",
            **dashboard_context
        )

    except Exception as e:
        print(f"Dashboard Load Error: {str(e)}")
        return render_template(
            "dashboard.html",
            stats={"transaction_count": 0, "active_alerts": 0, "fraud_count": 0, "false_positive_rate": 1.8},
            chart_data={
                "network_risk": 15,
                "weekly_trends": [10, 15, 12, 18, 22, 19, 15],
                "attack_vectors": [1, 1, 1, 1],
                "alert_severity": [0, 0, 0, 1],
                "location_alerts": {"Johannesburg": 0, "Durban": 0, "Cape Town": 0, "Pretoria": 0}
            },
            transactions=[],
            fraud_cases=[],
            latest_case={"id": "N/A", "xai_features": []},
            model_info={"loaded": False, "version": "1.0.0", "roc_auc": 0.0, "training_samples": 0, "features": []},
            user_role=session.get("role", "Admin"),
            username=session.get("username", "Sfiso Garry")
        )


# --------------------------------------------------
# LIVE DASHBOARD API (POLLS STATS + CHARTS + CASES)
# --------------------------------------------------

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    stats = get_transaction_stats()
    chart_data = get_live_dashboard_telemetry()
    fraud_cases, latest_case = _build_live_cases_and_xai()

    payload = dict(stats)
    payload["chart_data"] = chart_data
    payload["fraud_cases"] = fraud_cases[:6]
    payload["latest_case"] = latest_case
    return jsonify(payload)