import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mazi.db")

def get_db_connection():
    """Production-ready connection handler."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support (SQLite disables by default!)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_transaction_stats():
    """Get dashboard statistics from real data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {
        "total_transactions": cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
        "flagged_count": cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'Flagged'").fetchone()[0],
        "total_amount": cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions").fetchone()[0],
        "avg_risk_score": cursor.execute("SELECT COALESCE(AVG(risk_score), 0) FROM transactions").fetchone()[0],
        "fraud_count": cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 1").fetchone()[0]
    }
    
    conn.close()
    return stats

def get_recent_transactions(limit=10):
    """Get recent transactions for dashboard table."""
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions WHERE transaction_id = ?
    """, (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None