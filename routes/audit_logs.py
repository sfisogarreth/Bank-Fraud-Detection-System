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

audit_logs_bp = Blueprint(
    "audit_logs",
    __name__
)


# ==================================================
# AUDIT LOGS DASHBOARD
# ==================================================

@audit_logs_bp.route("/")
@login_required
@role_required("Admin")
def audit_logs():

    conn = get_db_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # LOAD AUDIT LOGS
    # --------------------------------------------------

    cursor.execute("""
        SELECT
            audit_logs.id,
            audit_logs.user_id,
            audit_logs.action,
            audit_logs.transaction_id,
            audit_logs.timestamp,
            users.username
        FROM audit_logs
        LEFT JOIN users
            ON audit_logs.user_id = users.id
        ORDER BY audit_logs.timestamp DESC
    """)

    logs = cursor.fetchall()

    # --------------------------------------------------
    # LOGIN EVENTS
    # --------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM audit_logs
        WHERE action LIKE '%Login%'
    """)

    login_count = (
        cursor.fetchone()["count"]
    )

    # --------------------------------------------------
    # FRAUD ACTIONS
    # --------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM audit_logs
        WHERE action LIKE '%Fraud%'
    """)

    fraud_actions = (
        cursor.fetchone()["count"]
    )

    # --------------------------------------------------
    # SETTINGS CHANGES
    # --------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM audit_logs
        WHERE action LIKE '%Settings%'
    """)

    settings_changes = (
        cursor.fetchone()["count"]
    )

    cursor.close()
    conn.close()

    return render_template(
        "audit_logs.html",
        logs=logs,
        login_count=login_count,
        fraud_actions=fraud_actions,
        settings_changes=settings_changes
    )