from flask import Blueprint, render_template, request, redirect, url_for
# Make sure to import the new update function we are about to create
from services.transaction_service import get_transaction_by_id, get_recent_cases, update_transaction_status

investigations_bp = Blueprint(
    "investigations",
    __name__
)

@investigations_bp.route("/investigations")
def investigation_logs():
    cases = get_recent_cases() 
    return render_template(
        "investigation_logs.html", 
        cases=cases
    )

@investigations_bp.route("/investigation/<int:transaction_id>")
def investigation(transaction_id):
    transaction = get_transaction_by_id(transaction_id)
    return render_template(
        "investigation.html",
        transaction=transaction
    )

# NEW ROUTE: Handles the POST request from the Confirm/Safe buttons
@investigations_bp.route("/investigation/<int:transaction_id>/resolve", methods=["POST"])
def resolve_investigation(transaction_id):
    # Get the value of the button that was clicked ('confirm' or 'safe')
    action = request.form.get("action")
    
    if action == "confirm":
        # Update DB to reflect confirmed fraud
        update_transaction_status(transaction_id, "Confirmed Fraud")
    elif action == "safe":
        # Update DB to clear the transaction
        update_transaction_status(transaction_id, "Cleared")
        
    # Send the operator back to the main investigation logs page after action is taken
    return redirect(url_for('investigations.investigation_logs'))