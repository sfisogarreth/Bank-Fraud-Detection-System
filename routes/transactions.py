from flask import Blueprint, render_template
# Import the function we just added to your database service
from services.transaction_service import get_all_transactions

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/transactions")
def transactions_list():
    # Fetch all transactions from the database
    all_tx = get_all_transactions()
    
    # Send them to your transactions.html template
    return render_template("transactions.html", transactions=all_tx)