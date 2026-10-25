import os
from config import Config
from database.connection import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = getattr(Config, 'DATABASE', os.path.join(BASE_DIR, 'mazi.db'))

def create_database():
    """Ensure the SQLite database file and base schema exist safely."""
    print(f"[*] Ensuring SQLite database exists at: {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            account_number TEXT,
            amount REAL,
            location TEXT,
            risk_score REAL DEFAULT 0,
            status TEXT DEFAULT 'Safe',
            is_fraud INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT DEFAULT 'PAYMENT',
            oldbalanceOrg REAL DEFAULT 0,
            newbalanceOrig REAL DEFAULT 0,
            oldbalanceDest REAL DEFAULT 0,
            newbalanceDest REAL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Customer',
            failed_attempts INTEGER DEFAULT 0,
            account_locked INTEGER DEFAULT 0,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            operator_name TEXT DEFAULT 'Fraud Analyst',
            email TEXT DEFAULT 'analyst@mazi.ai',
            fraud_threshold INTEGER DEFAULT 85,
            email_alerts INTEGER DEFAULT 1,
            critical_alerts INTEGER DEFAULT 1,
            weekly_reports INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            risk_score INTEGER,
            is_fraud INTEGER,
            model_version TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            transaction_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database tables initialized successfully.")

if __name__ == "__main__":
    create_database()