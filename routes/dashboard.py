from flask import Blueprint, render_template, jsonify
from services.transaction_service import get_transaction_stats, get_recent_transactions

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    stats = get_transaction_stats()
    recent = get_recent_transactions(10)
    return render_template("dashboard.html", stats=stats, transactions=recent)

@dashboard_bp.route('/api/stats')
def api_stats():
    """JSON endpoint for AJAX updates (live dashboard)."""
    return jsonify(get_transaction_stats())