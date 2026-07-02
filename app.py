from flask import Flask

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.investigations import investigations_bp
from routes.transactions import transactions_bp

from services.transaction_service import get_db_connection



app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)