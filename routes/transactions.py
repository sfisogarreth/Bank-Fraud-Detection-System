from flask import Blueprint, render_template
from services.transaction_service import get_all_transactions

transactions_bp = Blueprint(
    "transactions",
    __name__
)

@transactions_bp.route("/transactions")
def transactions():

    transactions_data = get_all_transactions()

    return render_template(
        "transactions.html",
        transactions=transactions_data
    )