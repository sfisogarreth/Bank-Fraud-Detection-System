from flask import Flask, render_template

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.investigations import investigations_bp
from routes.transactions import transactions_bp
from services.transaction_service import get_db_connection

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(investigations_bp)
app.register_blueprint(transactions_bp)

@app.route("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()
            return "✅ Database Connected Successfully"
    except Exception as e:
        return f"❌ Database Error: {e}"

# --- NEW ROUTES TO FIX NAVIGATION LINKS ---

@app.route("/risk-engine")
def risk_engine():
    return render_template("coming_soon.html", page_name="Risk Engine")

@app.route("/reports")
def reports():
    return render_template("coming_soon.html", page_name="System Reports")

@app.route("/settings")
def settings():
    return render_template("coming_soon.html", page_name="System Settings")

if __name__ == "__main__":
    app.run(debug=True)