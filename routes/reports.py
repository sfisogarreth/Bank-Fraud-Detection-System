from flask import (
    Blueprint,
    render_template
)

from database.connection import (
    get_db_connection
)

from services.security import (
    login_required,
    role_required
)

reports_bp = Blueprint(
    "reports",
    __name__
)


@reports_bp.route("/")
@login_required
@role_required(
    "Admin",
    "Manager"
)
def reports():

    conn = get_db_connection()
    cursor = conn.cursor()

    # -------------------------------
    # Total Transactions
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transactions
    """)

    total_transactions = (
        cursor.fetchone()["count"]
    )

    # -------------------------------
    # Confirmed Fraud
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transactions
        WHERE status='Confirmed_Fraud'
    """)

    confirmed_fraud = (
        cursor.fetchone()["count"]
    )

    # -------------------------------
    # Flagged Transactions
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transactions
        WHERE status='Flagged'
    """)

    flagged_transactions = (
        cursor.fetchone()["count"]
    )

    # -------------------------------
    # Total Amount
    # -------------------------------

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            ) AS total
        FROM transactions
    """)

    total_amount = (
        cursor.fetchone()["total"]
        or 0
    )

    # -------------------------------
    # Average Risk
    # -------------------------------

    cursor.execute("""
        SELECT
            AVG(risk_score)
            AS avg_risk
        FROM transactions
    """)

    avg_risk = (
        cursor.fetchone()["avg_risk"]
        or 0
    )

    # -------------------------------
    # Recent Fraud Cases
    # -------------------------------

    cursor.execute("""
        SELECT
            transaction_id,
            account_number,
            amount,
            risk_score,
            timestamp
        FROM transactions
        WHERE status='Confirmed_Fraud'
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    recent_fraud_cases = (
        cursor.fetchall()
    )

    fraud_rate = 0

    if total_transactions > 0:

        fraud_rate = round(
            (
                confirmed_fraud /
                total_transactions
            ) * 100,
            2
        )

    report = {

        "total_transactions":
            total_transactions,

        "confirmed_fraud":
            confirmed_fraud,

        "flagged_transactions":
            flagged_transactions,

        "total_amount":
            round(total_amount, 2),

        "avg_risk":
            round(avg_risk, 2),

        "fraud_rate":
            fraud_rate

    }

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        report=report,
        recent_fraud_cases=recent_fraud_cases
    )