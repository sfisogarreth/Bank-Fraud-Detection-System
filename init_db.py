import os
import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = getattr(Config, 'DATABASE', os.path.join(BASE_DIR, 'mazi.db'))


def ensure_schema_upgrades():
    """
    Non-destructively upgrades an existing mazi.db by adding the 'explanation' column
    and high-speed indexes if they do not exist yet, without wiping existing transactions.
    """
    if not os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "explanation" not in columns:
            cursor.execute(
                "ALTER TABLE transactions ADD COLUMN explanation TEXT DEFAULT 'Evaluated by MAZI Hybrid ML + C++ Velocity Engine.'"
            )
            print("✅ Added 'explanation' column to existing transactions table.")

        # Ensure high-speed indexes exist on existing database
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_risk ON transactions(risk_score DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);")
        conn.commit()
    except Exception as e:
        print(f"Schema upgrade note: {e}")
    finally:
        cursor.close()
        conn.close()


def setup_database():
    if os.path.exists(DB_PATH):
        print("Removing old database...")
        os.remove(DB_PATH)
    
    print("Creating new SQLite database with full MAZI schema and performance indexes...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Transactions table (with explanation column)
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
            newbalanceDest REAL DEFAULT 0,
            explanation TEXT DEFAULT 'Evaluated by MAZI Hybrid ML + C++ Velocity Engine.'
        )
    ''')
    print("Transactions table created.")

    # 2. Users table
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
    print("Users table created.")

    # 3. Settings table
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
    print("Settings table created.")

    # 4. Fraud predictions table
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
    print("Fraud_predictions table created.")

    # 5. Audit logs table
    cursor.execute('''
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            transaction_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Audit_logs table created.")

    # 6. High-Speed Database Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_risk ON transactions(risk_score DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);")
    print("High-speed SQLite indexes created.")

    # Seed initial test transactions with dynamic explanations
    cursor.executemany('''
        INSERT INTO transactions (
            transaction_id, account_number, amount, location, risk_score,
            status, is_fraud, type, oldbalanceOrg, newbalanceOrig, explanation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('TXN1001', 'ACC-7782', 12500.00, 'Johannesburg, ZA', 92, 'Flagged', 1, 'TRANSFER', 13000.00, 500.00,
         'CRITICAL RISK: 96.2% account balance drain via TRANSFER | High-value anomaly (R12,500.00).'),
        ('TXN1002', 'ACC-9921', 450.00, 'Cape Town, ZA', 12, 'Safe', 0, 'PAYMENT', 15000.00, 14550.00,
         'LOW RISK: Routine PAYMENT of R450.00 (3.0% of available balance) within normal baseline.'),
        ('TXN1003', 'ACC-4451', 8900.00, 'Durban, ZA', 78, 'Flagged', 1, 'CASH_OUT', 10000.00, 1100.00,
         'HIGH RISK: Rapid CASH_OUT draining 89.0% of account balance.'),
        ('TXN1004', 'ACC-2210', 3200.00, 'Pretoria, ZA', 45, 'Safe', 0, 'PAYMENT', 22000.00, 18800.00,
         'MODERATE-LOW RISK: Standard payment within normal account velocity.'),
        ('TXN1005', 'ACC-6677', 50000.00, 'Johannesburg, ZA', 96, 'Confirmed_Fraud', 1, 'TRANSFER', 50000.00, 0.00,
         'CRITICAL FRAUD: 100% full account balance depletion (R50,000.00) via single TRANSFER.'),
    ])
    print("5 seed transactions inserted.")

    # Seed Admin User (Sfiso Garry) + Default Manager
    admin_hash = generate_password_hash('Maybe12345&', method='pbkdf2:sha256')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('Sfiso Garry', 'sfiso_garry@mazi.ai', admin_hash, 'Admin'))
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@mazi.ai', generate_password_hash('admin123', method='pbkdf2:sha256'), 'Manager'))
    print("Admin user created (sfiso_garry@mazi.ai / Maybe12345&).")

    # Seed Default Settings
    cursor.execute('''
        INSERT INTO settings (user_id, operator_name, email, fraud_threshold, email_alerts, critical_alerts, weekly_reports)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (1, 'Fraud Analyst', 'analyst@mazi.ai', 85, 1, 1, 0))
    print("Default operator settings inserted.")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ Database ready at: " + DB_PATH)


if __name__ == "__main__":
    setup_database()