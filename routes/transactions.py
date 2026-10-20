from flask import (
    Blueprint,
    render_template,
    session
)

from services.transaction_service import (
    get_recent_transactions,
    get_transaction_by_id
)

from services.security import (
    login_required
)

transactions_bp = Blueprint(
    'transactions',
    __name__
)


# ==================================================
# TRANSACTIONS LIST
# ==================================================

@transactions_bp.route('/')
@login_required
def transactions_list():
    """
    Show transactions based on user role.
    """

    role = session.get("role", "Customer")
    user_id = session.get("user_id")

    # CUSTOMER VIEW
    # Later we will replace this with:
    # get_customer_transactions(user_id)
    if role == "Customer":

        transactions = get_recent_transactions(20)

    # ADMIN / MANAGER VIEW
    else:

        transactions = get_recent_transactions(50)

    return render_template(
        "transactions.html",
        transactions=transactions,
        user_role=role,
        username=session.get("username")
    )


# ==================================================
# TRANSACTION DETAILS
# ==================================================

@transactions_bp.route('/<transaction_id>')
@login_required
def transaction_detail(transaction_id):
    """
    Show details for a single transaction.
    """

    role = session.get("role", "Customer")

    txn = get_transaction_by_id(transaction_id)

    if txn is None:

        return render_template(
            "coming_soon.html",
            page_name=f"Transaction {transaction_id} Not Found"
        ), 404

    return render_template(
        "transactions.html",
        transaction=txn,
        user_role=role,
        username=session.get("username")
    )