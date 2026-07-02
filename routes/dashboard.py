from flask import Blueprint
from flask import render_template

from services.transaction_service import (
    get_transaction_count,
    get_recent_cases
)

from services.xai_engine import (
    generate_explanation
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route('/')
def dashboard():

    count = get_transaction_count()

    cases = get_recent_cases()

    stats = {

        "transaction_count":
            f"{count:,}",

        "active_alerts":
            len(cases),

        "false_positive_rate":
            1.8
    }

    latest_case = generate_explanation(
        cases[0]
    )

    return render_template(
        "dashboard.html",

        stats=stats,

        fraud_cases=cases,

        latest_case=latest_case
    )