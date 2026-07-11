from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.transaction_service import (
    get_recent_cases, 
    get_transaction_by_int_id,
    update_transaction_status,
    get_flagged_transactions
)

investigations_bp = Blueprint('investigations', __name__)

@investigations_bp.route('/')
def investigation_logs():
    """Show investigation logs page."""
    cases = get_flagged_transactions(20)

    # Format for template
    formatted_cases = []
    for case in cases:
        formatted_cases.append({
            'id': case['id'],
            'risk_score': case['risk_score'],
            'type': 'Account Takeover' if case['risk_score'] > 90 else 'Card Fraud' if case['risk_score'] > 80 else 'Suspicious Activity',
            'loss': f"{case['amount']:,.2f}"
        })

    return render_template("investigation_logs.html", cases=formatted_cases)

@investigations_bp.route('/<int:id>')
def investigation_detail(id):
    """Show investigation detail page."""
    transaction = get_transaction_by_int_id(id)
    if transaction is None:
        return render_template("coming_soon.html", page_name=f"Case #{id} Not Found"), 404
    return render_template("investigation.html", transaction=transaction)

@investigations_bp.route('/<int:id>/resolve', methods=['POST'])
def resolve_case(id):
    """Handle resolve action from investigation page."""
    action = request.form.get('action')
    transaction = get_transaction_by_int_id(id)

    if transaction is None:
        return render_template("coming_soon.html", page_name="Case Not Found"), 404

    if action == 'confirm':
        update_transaction_status(transaction['transaction_id'], 'Confirmed_Fraud')
    elif action == 'safe':
        update_transaction_status(transaction['transaction_id'], 'Safe')

    return redirect('/investigations/')