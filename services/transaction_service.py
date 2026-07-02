import sqlite3

DATABASE = "mazi.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_transaction_count():
    conn = get_db_connection()
    result = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM transactions
        """
    ).fetchone()
    conn.close()
    return result["total"]

def get_recent_cases():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT *
        FROM transactions
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()
    conn.close()
    return rows

def get_all_transactions():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return rows

def get_transaction_by_id(transaction_id):
    conn = get_db_connection()
    transaction = conn.execute(
        """
        SELECT *
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,)
    ).fetchone()
    conn.close()
    return transaction

def update_transaction_status(transaction_id, new_status):
    """
    Updates the status of a specific transaction in the database.
    """
    try:
        conn = get_db_connection()
        
        # Parameterized query using ? for SQLite to prevent SQL injection
        conn.execute(
            """
            UPDATE transactions 
            SET status = ? 
            WHERE id = ?
            """, 
            (new_status, transaction_id)
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Database Error: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()