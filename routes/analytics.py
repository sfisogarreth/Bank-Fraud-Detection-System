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

    # ------------------------------------------
    # Total Transactions
    # ------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM transactions
        """
    )

    total_transactions = (
        cursor.fetchone()["count"]
    )

    # ------------------------------------------
    # Total Fraud
    # ------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM transactions
        WHERE is_fraud = 1
        """
    )

    total_fraud = (
        cursor.fetchone()["count"]
    )

    # ------------------------------------------
    # Confirmed Fraud Cases
    # ------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM transactions
        WHERE status = 'Confirmed_Fraud'
        """
    )

    confirmed_fraud = (
        cursor.fetchone()["count"]
    )

    # ------------------------------------------
    # Average Risk Score
    # ------------------------------------------

    cursor.execute(
        """
        SELECT AVG(risk_score) AS risk
        FROM transactions
        """
    )

    avg_risk = (
        cursor.fetchone()["risk"]
        or 0
    )

    # ------------------------------------------
    # Total Money Processed
    # ------------------------------------------

    cursor.execute(
        """
        SELECT SUM(amount) AS total
        FROM transactions
        """
    )

    total_amount = (
        cursor.fetchone()["total"]
        or 0
    )

    # ------------------------------------------
    # Fraud Prevented (FIXED CRASH HERE)
    # ------------------------------------------

    cursor.execute(
        """
        SELECT SUM(amount) AS prevented
        FROM transactions
        WHERE status IN ('Confirmed_Fraud', 'Intercepted', 'Flagged')
        """
    )

    prevented_result = cursor.fetchone()

    fraud_prevented = (
        prevented_result["prevented"]
        if prevented_result and prevented_result["prevented"]
        else 0
    )

    # ------------------------------------------
    # Fraud Rate
    # ------------------------------------------

    fraud_rate = 0

    if total_transactions > 0:

        fraud_rate = round(
            (
                total_fraud
                / total_transactions
            ) * 100,
            2
        )

    stats = {

        "total_transactions":
            total_transactions,

        "total_fraud":
            total_fraud,

        "confirmed_fraud":
            confirmed_fraud,

        "avg_risk":
            round(avg_risk, 2),

        "fraud_rate":
            fraud_rate,

        "total_amount":
            round(total_amount, 2),

        "fraud_prevented":
            round(fraud_prevented, 2)

    }

    cursor.close()
    conn.close()

    return render_template(
        "analytics.html",
        stats=stats,
        username=session.get("username"),
        user_role=session.get("role")
    )