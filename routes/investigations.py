from flask import Blueprint, render_template
from services.transaction_service import get_transaction_by_id

investigations_bp = Blueprint(
    "investigations",
    __name__
)

@investigations_bp.route(
    "/investigation/<int:transaction_id>"
)
def investigation(transaction_id):

    transaction = get_transaction_by_id(
        transaction_id
    )

    return render_template(
        "investigation.html",
        transaction=transaction
    )