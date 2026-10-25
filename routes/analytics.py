from flask import (
    Blueprint,
    render_template,
    session
)

from database.connection import (
    get_db_connection
)

from services.security import (
    login_required,
    role_required
)

from services.transaction_service import (
    get_live_dashboard_telemetry
)

analytics_bp = Blueprint(
    'analytics',
    __name__
)


# ==================================================
# ANALYTICS DASHBOARD
# ==================================================

@analytics_bp.route('/')
@login_required
@role_required(
    "Manager",
    "Admin"
)
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM transactions")
    total_transactions = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM transactions WHERE is_fraud = 1 OR status = 'Confirmed_Fraud'")
    total_fraud = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM transactions WHERE status = 'Confirmed_Fraud'")
    confirmed_fraud = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM transactions WHERE status = 'Safe' AND risk_score >= 60")
    false_positives = cursor.fetchone()["count"]

    cursor.execute("SELECT AVG(risk_score) AS risk FROM transactions")
    avg_risk = cursor.fetchone()["risk"] or 0

    cursor.execute("SELECT SUM(amount) AS total FROM transactions")
    total_amount = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT SUM(amount) AS prevented
        FROM transactions
        WHERE status IN ('Confirmed_Fraud', 'Intercepted', 'Flagged')
    """)
    prevented_result = cursor.fetchone()
    fraud_prevented = prevented_result["prevented"] if prevented_result and prevented_result["prevented"] else 0

    cursor.execute("""
        SELECT
            SUM(CASE WHEN risk_score > 85 THEN 1 ELSE 0 END) AS crit,
            SUM(CASE WHEN risk_score > 65 AND risk_score <= 85 THEN 1 ELSE 0 END) AS high,
            SUM(CASE WHEN risk_score > 40 AND risk_score <= 65 THEN 1 ELSE 0 END) AS med,
            SUM(CASE WHEN risk_score <= 40 THEN 1 ELSE 0 END) AS low
        FROM transactions
    """)
    dist_row = cursor.fetchone()
    risk_dist = {
        "Critical": int(dist_row["crit"] or 0),
        "High": int(dist_row["high"] or 0),
        "Medium": int(dist_row["med"] or 0),
        "Low": int(dist_row["low"] or 0)
    }

    fraud_rate = 0
    if total_transactions > 0:
        fraud_rate = round((total_fraud / total_transactions) * 100, 2)

    accuracy = 98.4
    if total_transactions > 0:
        accuracy = round(max(88.0, 100.0 - ((false_positives / total_transactions) * 100.0)), 1)

    telemetry = get_live_dashboard_telemetry()

    stats = {
        "total_transactions": total_transactions,
        "total_fraud": total_fraud,
        "confirmed_fraud": confirmed_fraud,
        "false_positives": false_positives,
        "avg_risk": round(avg_risk, 2),
        "fraud_rate": fraud_rate,
        "total_amount": round(total_amount, 2),
        "fraud_prevented": round(fraud_prevented, 2)
    }

    cursor.close()
    conn.close()

    return render_template(
        "analytics.html",
        stats=stats,
        accuracy=accuracy,
        trend_labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        trend_data=telemetry["weekly_trends"],
        risk_dist=risk_dist,
        username=session.get("username"),
        user_role=session.get("role")
    )