import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "mazi.db"

def init_database():
    """Create all tables and seed with realistic demo data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables for clean setup
    cursor.executescript("""
        DROP TABLE IF EXISTS investigations;
        DROP TABLE IF EXISTS fraud_predictions;
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS users;
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Transactions table (your core data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            account_number TEXT NOT NULL,
            amount REAL NOT NULL,
            location TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            risk_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Safe',
            is_fraud INTEGER DEFAULT 0
        )
    """)

    # Fraud predictions (audit trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            is_fraud INTEGER NOT NULL,
            model_version TEXT DEFAULT '1.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Investigations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            assigned_to INTEGER,
            status TEXT DEFAULT 'Open',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)

    # Seed users
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, email, password_hash, role)
        VALUES 
        (1, 'admin', 'admin@mazi.com', 'hashed_admin_pass', 'admin'),
        (2, 'analyst1', 'analyst@mazi.com', 'hashed_analyst_pass', 'analyst')
    """)

    # Seed realistic transactions
    accounts = [f'ACC{str(i).zfill(3)}' for i in range(1, 21)]
    locations = ['New York', 'London', 'Lagos', 'Tokyo', 'Cape Town', 'Berlin', 'Paris', 'Johannesburg', 'Durban', 'Pretoria']

    for i in range(50):
        acc = random.choice(accounts)
        amount = round(random.uniform(10, 25000), 2)
        # Make some transactions suspicious
        is_fraud = 1 if amount > 15000 and random.random() > 0.3 else 0
        status = 'Flagged' if is_fraud else 'Safe'
        risk_score = random.randint(75, 98) if is_fraud else random.randint(5, 45)

        time_offset = timedelta(hours=random.randint(0, 168))
        timestamp = (datetime.now() - time_offset).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO transactions (transaction_id, account_number, amount, location, timestamp, risk_score, status, is_fraud)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (f'TXN{1000+i}', acc, amount, random.choice(locations), timestamp, risk_score, status, is_fraud))

    conn.commit()
    conn.close()
    print("✅ Database initialized with 50 transactions, 2 users, and full schema.")

if __name__ == "__main__":
    init_database()