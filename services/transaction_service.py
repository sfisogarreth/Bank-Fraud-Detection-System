import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mazi.db")


def get_db_connection():
    """Create a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_transaction_stats():
    """Pull real numbers from the database for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {
        "total_transactions": cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
        "flagged_count": cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'Flagged'").fetchone()[0],
        "total_amount": round(cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions").fetchone()[0], 2),
        "avg_risk_score": round(cursor.execute("SELECT COALESCE(AVG(risk_score), 0) FROM transactions").fetchone()[0], 2),
        "fraud_count": cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 1").fetchone()[0]
    }
    
    conn.close()
    return stats


def get_recent_transactions(limit=10):
    """Get the latest transactions for the dashboard table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT transaction_id, account_number, amount, location, 
               risk_score, status, timestamp
        FROM transactions
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transaction_by_id(transaction_id):
    """Get a single transaction's full details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# --- NEW FUNCTIONS FOR INVESTIGATIONS ---

def get_recent_cases(limit=20):
    """Get flagged/fraud transactions that need investigation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT transaction_id, account_number, amount, location, 
               risk_score, status, timestamp, is_fraud
        FROM transactions
        WHERE status IN ('Flagged', 'Confirmed_Fraud', 'Reviewing')
        ORDER BY risk_score DESC, timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_transaction_status(transaction_id, new_status):
    """Update a transaction's status (e.g., Safe -> Flagged -> Confirmed_Fraud)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validate status to prevent garbage data
    valid_statuses = ['Safe', 'Flagged', 'Confirmed_Fraud', 'Reviewing']
    if new_status not in valid_statuses:
        conn.close()
        return False
    
    cursor.execute("""
        UPDATE transactions 
        SET status = ? 
        WHERE transaction_id = ?
    """, (new_status, transaction_id))
    
    conn.commit()
    updated = cursor.rowcount > 0  # True if a row was actually updated
    conn.close()
    return updated