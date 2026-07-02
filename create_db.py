import sqlite3

conn = sqlite3.connect("mazi.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    account_number TEXT,
    amount REAL,
    risk_score INTEGER,
    status TEXT
)
""")

cursor.execute("""
INSERT OR REPLACE INTO transactions
(id, account_number, amount, risk_score, status)
VALUES
(1001, 'ACC001', 2500, 45, 'Safe')
""")

cursor.execute("""
INSERT OR REPLACE INTO transactions
(id, account_number, amount, risk_score, status)
VALUES
(1002, 'ACC002', 15000, 91, 'Flagged')
""")

conn.commit()

conn.close()

print("Database Created Successfully!")