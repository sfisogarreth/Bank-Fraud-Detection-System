from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import joblib
import os

try:
    import fast_math
except ImportError:
    print("Warning: fast_math C++ module not compiled. Using mock logic.")

app = Flask(__name__)

# System Model Paths Configuration
model_path = os.path.join(os.path.dirname(__file__), "core_ml", "fraud_model.pkl")
ai_model = None
if os.path.exists(model_path):
    ai_model = joblib.load(model_path)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",                 
        password="Maybe114031997&",  
        database="mazi_fraud_db"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Here you would add production database verification logic
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Here you would add production database saving logic
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        result = cursor.fetchone()
        tx_count = result['total'] if result else 0
        
        cursor.execute("SELECT * FROM fraud_cases LIMIT 5")
        recent_cases = cursor.fetchall()
        
        conn.close()
    except mysql.connector.Error:
        tx_count = 14820
        recent_cases = [
            {"id": 2000109, "type": "Velocity Exploit", "status": "Intercepted", "loss": 1800},
            {"id": 2000160, "type": "Account Takeover", "status": "Under Review", "loss": 1131},
        ]

    stats = {"transaction_count": tx_count}
    return render_template('dashboard.html', stats=stats, fraud_cases=recent_cases)

if __name__ == '__main__':
    app.run(debug=True)