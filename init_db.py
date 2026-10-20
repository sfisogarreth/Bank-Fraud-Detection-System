import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mazi.db')

def setup_database():
    if os.path.exists(DB_PATH):
        print("Removing old database...")
        os.remove(DB_PATH)
    
    print("Creating new SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE transactions (
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
    print("transactions table created.")

    cursor.execute('''
        CREATE TABLE users (

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
    print("users table created.")

    cursor.execute('''
        CREATE TABLE settings (
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
    print("settings table created.")

    cursor.execute('''
        CREATE TABLE fraud_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            risk_score INTEGER,
            is_fraud INTEGER,
            model_version TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("fraud_predictions table created.")

    cursor.execute('''
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            transaction_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("audit_logs table created.")

    cursor.executemany('''
        INSERT INTO transactions (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('TXN1001', 'ACC-7782', 12500.00, 'Johannesburg', 92, 'Flagged', 1, 'TRANSFER'),
        ('TXN1002', 'ACC-9921', 450.00, 'Cape Town', 12, 'Safe', 0, 'PAYMENT'),
        ('TXN1003', 'ACC-4451', 8900.00, 'Durban', 78, 'Flagged', 0, 'CASH_OUT'),
        ('TXN1004', 'ACC-2210', 3200.00, 'Pretoria', 45, 'Safe', 0, 'PAYMENT'),
        ('TXN1005', 'ACC-6677', 50000.00, 'Johannesburg', 96, 'Confirmed_Fraud', 1, 'TRANSFER'),
    ])
    print("5 seed transactions inserted.")

    from werkzeug.security import generate_password_hash
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@mazi.ai', generate_password_hash('admin123', method='pbkdf2:sha256'), 'Manager'))
    print("Admin user created (admin / admin123).")

    cursor.execute('''
        INSERT INTO settings (user_id, operator_name, email, fraud_threshold, email_alerts, critical_alerts, weekly_reports)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (1, 'Fraud Analyst', 'analyst@mazi.ai', 85, 1, 1, 0))
    print("Default settings inserted.")

    conn.commit()
    cursor.close()
    conn.close()
    print("\nDatabase ready at: " + DB_PATH)
    print("Login: admin@mazi.ai / admin123")

if __name__ == "__main__":
    setup_database()