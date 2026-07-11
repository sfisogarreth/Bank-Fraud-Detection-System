import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Logging setup
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.investigations import investigations_bp
from routes.transactions import transactions_bp

# Register with URL prefixes (professional API structure)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(analytics_bp, url_prefix='/analytics')
app.register_blueprint(investigations_bp, url_prefix='/investigations')
app.register_blueprint(transactions_bp, url_prefix='/transactions')

# Root route - redirect to dashboard
@app.route("/")
def index():
    return redirect("/dashboard/")

# Database health check
@app.route("/db-test")
def db_test():
    try:
        from services.transaction_service import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            "status": "connected",
            "database": "SQLite",
            "transactions_count": count,
            "message": "✅ Database Connected Successfully"
        })
    except Exception as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Health check (required for deployment monitoring)
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "mazi-fraud-api",
        "timestamp": datetime.now().isoformat(),
        "database": "SQLite"
    })

# Coming soon pages (keep your existing routes)
@app.route("/risk-engine")
def risk_engine():
    return render_template("coming_soon.html", page_name="Risk Engine")

@app.route("/reports")
def reports():
    return render_template("coming_soon.html", page_name="System Reports")

@app.route("/settings")
def settings():
    return render_template("coming_soon.html", page_name="System Settings")

# Global error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("coming_soon.html", page_name="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Use host='0.0.0.0' so it works on your network for demos
    app.run(host='0.0.0.0', port=5000, debug=True)