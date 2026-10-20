from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)

from services.transaction_service import (
    get_recent_cases,
    get_transaction_by_int_id,
    update_transaction_status,
    get_flagged_transactions
)

from services.security import (
    login_required,
    role_required
)

from database.connection import (
    get_db_connection
)

investigations_bp = Blueprint(
    'investigations',
    __name__
)


# ==================================================
# AUDIT LOG HELPER
# ==================================================

def log_audit(user_id, action, transaction_id=None):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO audit_logs
            (
                user_id,
                action,
                transaction_id
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                action,
                transaction_id
            )
        )

        conn.commit()

    finally:

        cursor.close()
        conn.close()


# ==================================================
# INVESTIGATIONS
# ==================================================

@investigations_bp.route('/')
@login_required
@role_required("Admin", "Manager")
def investigations():

    cases = get_flagged_transactions(20)

    formatted_cases = []

    for case in cases:

        formatted_cases.append({
            "id": case["id"],
            "risk_score": case["risk_score"],
            "type": (
                "Account Takeover"
                if case["risk_score"] > 90
                else "Card Fraud"
                if case["risk_score"] > 80
                else "Suspicious Activity"
            ),
            "loss": f"{case['amount']:,.2f}"
        })

    return render_template(
        "investigation_logs.html",
        cases=formatted_cases,
        user_role=session.get("role")
    )


# ==================================================
# INVESTIGATION DETAIL
# ==================================================

@investigations_bp.route('/<int:id>')
@login_required
@role_required("Admin", "Manager")
def investigation_detail(id):

    raw_transaction = get_transaction_by_int_id(id)

    if raw_transaction is None:

        return render_template(
            "coming_soon.html",
            page_name=f"Case #{id} Not Found"
        ), 404

    transaction = {
        "id": raw_transaction.get("id", id),
        "transaction_id": raw_transaction.get("transaction_id", f"TXN-{id}"),
        "account_number": raw_transaction.get("account_number", "N/A"),
        "amount": f"{raw_transaction.get('amount', 0.0):.2f}",
        "risk_score": raw_transaction.get("risk_score", 0),
        "status": raw_transaction.get("status", "Unknown")
    }

    return render_template(
        "investigation.html",
        transaction=transaction,
        user_role=session.get("role")
    )


# ==================================================
# RESOLVE CASE
# ==================================================

@investigations_bp.route('/<int:id>/resolve', methods=['POST'])
@login_required
@role_required("Admin", "Manager")
def resolve_case(id):

    action = request.form.get("action")

    transaction = get_transaction_by_int_id(id)

    if transaction is None:

        flash(
            "Case not found.",
            "error"
        )

        return redirect("/investigations/")
        
    tx_id = transaction.get("transaction_id", id)

    if action == "confirm":

        update_transaction_status(
            tx_id,
            "Confirmed_Fraud"
        )

        log_audit(
            session.get("user_id"),
            "Confirmed Fraud",
            tx_id
        )

        flash(
            f"Case #{id} confirmed as fraud.",
            "success"
        )

    elif action == "safe":

        update_transaction_status(
            tx_id,
            "Safe"
        )

        log_audit(
            session.get("user_id"),
            "Marked Safe",
            tx_id
        )

        flash(
            f"Case #{id} marked as safe.",
            "success"
        )

    else:

        flash(
            "Invalid action.",
            "error"
        )

    return redirect("/investigations/")