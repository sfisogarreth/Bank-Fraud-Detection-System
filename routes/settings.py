import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from database.connection import (
    get_db_connection
)

from services.security import (
    login_required,
    role_required
)

settings_bp = Blueprint(
    "settings",
    __name__
)


# ==================================================
# AUDIT LOGGING
# ==================================================

def log_audit(user_id, action):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO audit_logs
            (
                user_id,
                action
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                action
            )
        )

        conn.commit()

    finally:

        cursor.close()
        conn.close()


# ==================================================
# SETTINGS PAGE
# ==================================================

@settings_bp.route(
    "/",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin")
def settings():

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        fraud_threshold = request.form.get(
            "threshold",
            85
        )

        email_alerts = (
            1 if request.form.get("email_alerts")
            else 0
        )

        critical_alerts = (
            1 if request.form.get("critical_alerts")
            else 0
        )

        weekly_reports = (
            1 if request.form.get("weekly_reports")
            else 0
        )

        operator_name = request.form.get(
            "operator_name",
            ""
        ).strip()

        operator_email = request.form.get(
            "email",
            ""
        ).strip()

        try:

            fraud_threshold = int(
                fraud_threshold
            )

            if fraud_threshold < 1:
                fraud_threshold = 1

            if fraud_threshold > 100:
                fraud_threshold = 100

            cursor.execute(
                """
                UPDATE settings
                SET
                    fraud_threshold=?,
                    email_alerts=?,
                    critical_alerts=?,
                    weekly_reports=?,
                    operator_name=?,
                    email=?
                WHERE id=1
                """,
                (
                    fraud_threshold,
                    email_alerts,
                    critical_alerts,
                    weekly_reports,
                    operator_name,
                    operator_email
                )
            )

            conn.commit()

            log_audit(
                session.get("user_id"),
                "Updated System Settings"
            )

            flash(
                "Settings updated successfully.",
                "success"
            )

        except Exception as e:

            conn.rollback()

            flash(
                f"Failed to update settings: {e}",
                "error"
            )

        finally:

            pass

        return redirect(
            url_for(
                "settings.settings"
            )
        )

    # ------------------------------------------------
    # LOAD SETTINGS & SYSTEM STATUS
    # ------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM settings
        WHERE id = 1
        """
    )

    settings_data = cursor.fetchone()

    try:
        cursor.execute("SELECT COUNT(*) AS count FROM transactions")
        db_count_result = cursor.fetchone()
        db_count = db_count_result["count"] if db_count_result else 0
    except:
        db_count = 0

    cursor.close()
    conn.close()

    try:
        from services.prediction_service import get_model_info
        model_info = get_model_info()
        model_loaded = model_info.get("loaded", False)
    except ImportError:
        model_loaded = False

    return render_template(
        "settings.html",
        settings=settings_data,
        username=session.get("username"),
        user_role=session.get("role"),
        db_count=db_count,
        model_loaded=model_loaded,
        now=datetime.datetime.now().strftime("%Y-%m-%d")
    )