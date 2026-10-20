
from database.connection import get_db_connection


# ==================================================
# DATABASE HELPER
# ==================================================

def execute_query(query, params=(), fetch_one=False):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(query, params)

        if fetch_one:

            row = cursor.fetchone()

            if row:
                return dict(row)

            return None

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        cursor.close()
        conn.close()


# ==================================================
# DASHBOARD STATISTICS
# ==================================================

def get_transaction_stats():

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM transactions
        """)

        total_transactions = (
            cursor.fetchone()["count"]
        )

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM transactions
            WHERE status = 'Flagged'
        """)

        flagged_count = (
            cursor.fetchone()["count"]
        )

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM transactions
            WHERE is_fraud = 1
        """)

        fraud_count = (
            cursor.fetchone()["count"]
        )

        cursor.execute("""
            SELECT COALESCE(
                SUM(amount),
                0
            ) AS total
            FROM transactions
        """)

        total_amount = round(
            cursor.fetchone()["total"],
            2
        )

        cursor.execute("""
            SELECT COALESCE(
                AVG(risk_score),
                0
            ) AS avg
            FROM transactions
        """)

        avg_risk_score = round(
            cursor.fetchone()["avg"],
            2
        )

        fraud_rate = 0

        if total_transactions > 0:

            fraud_rate = round(
                (
                    fraud_count /
                    total_transactions
                ) * 100,
                2
            )

        return {

            "total_transactions":
                total_transactions,

            "transaction_count":
                total_transactions,

            "flagged_count":
                flagged_count,

            "active_alerts":
                flagged_count,

            "fraud_count":
                fraud_count,

            "fraud_rate":
                fraud_rate,

            "total_amount":
                total_amount,

            "avg_risk_score":
                avg_risk_score,

            "false_positive_rate":
                1.8
        }

    finally:

        cursor.close()
        conn.close()


# ==================================================
# RECENT TRANSACTIONS
# ==================================================

def get_recent_transactions(limit=10):

    return execute_query(
        """
        SELECT
            id,
            transaction_id,
            account_number,
            amount,
            location,
            risk_score,
            status,
            timestamp
        FROM transactions
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )


# ==================================================
# CUSTOMER TRANSACTIONS
# ==================================================

def get_customer_transactions(
    account_number,
    limit=20
):

    return execute_query(
        """
        SELECT *
        FROM transactions
        WHERE account_number = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (
            account_number,
            limit
        )
    )


# ==================================================
# SINGLE TRANSACTION LOOKUP
# ==================================================

def get_transaction_by_id(transaction_id):

    return execute_query(
        """
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
        """,
        (transaction_id,),
        fetch_one=True
    )


def get_transaction_by_int_id(id):

    return execute_query(
        """
        SELECT *
        FROM transactions
        WHERE id = ?
        """,
        (id,),
        fetch_one=True
    )


# ==================================================
# INVESTIGATION CASES
# ==================================================

def get_recent_cases(limit=20):

    return execute_query(
        """
        SELECT
            id,
            transaction_id,
            account_number,
            amount,
            location,
            risk_score,
            status,
            timestamp,
            is_fraud
        FROM transactions
        WHERE status IN
        (
            'Flagged',
            'Confirmed_Fraud',
            'Reviewing'
        )
        ORDER BY
            risk_score DESC,
            timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )


# ==================================================
# FLAGGED TRANSACTIONS
# ==================================================

def get_flagged_transactions(limit=50):

    return execute_query(
        """
        SELECT
            id,
            transaction_id,
            account_number,
            amount,
            location,
            risk_score,
            status,
            timestamp
        FROM transactions
        WHERE status IN
        (
            'Flagged',
            'Confirmed_Fraud'
        )
        ORDER BY risk_score DESC
        LIMIT ?
        """,
        (limit,)
    )


# ==================================================
# UPDATE STATUS
# ==================================================

def update_transaction_status(
    transaction_id,
    new_status
):

    valid_statuses = [
        "Safe",
        "Flagged",
        "Confirmed_Fraud",
        "Reviewing"
    ]

    if new_status not in valid_statuses:
        return False

    fraud_value = (
        1
        if new_status == "Confirmed_Fraud"
        else 0
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE transactions
            SET
                status = ?,
                is_fraud = ?
            WHERE transaction_id = ?
            """,
            (
                new_status,
                fraud_value,
                transaction_id
            )
        )

        conn.commit()

        return (
            cursor.rowcount > 0
        )

    finally:

        cursor.close()
        conn.close()