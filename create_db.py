import mysql.connector
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 3306))
}

def create_database():
    """Create the mazi_fraud_db database if it doesn't exist."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS mazi_fraud_db")
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database 'mazi_fraud_db' created (or already exists)")

def init_tables():
    """Create all tables and seed with demo data."""
    conn = mysql.connector.connect(database="mazi_fraud_db", **DB_CONFIG)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    tables = ['investigations', 'fraud_predictions', 'transactions', 'users', 'settings']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Users table
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('analyst', 'admin', 'investigator') DEFAULT 'analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Settings table
    cursor.execute("""
        CREATE TABLE settings (
            user_id INT PRIMARY KEY,
            operator_name VARCHAR(100) DEFAULT 'Fraud Analyst',
            email VARCHAR(100) DEFAULT 'analyst@mazi.ai',
            fraud_threshold INT DEFAULT 85,
            email_alerts TINYINT DEFAULT 1,
            critical_alerts TINYINT DEFAULT 1,
            weekly_reports TINYINT DEFAULT 0,
            theme VARCHAR(20) DEFAULT 'dark',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id VARCHAR(50) UNIQUE NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            amount DECIMAL(15, 2) NOT NULL,
            location VARCHAR(100),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            risk_score INT DEFAULT 0,
            status ENUM('Safe', 'Flagged', 'Confirmed_Fraud', 'Reviewing') DEFAULT 'Safe',
            is_fraud TINYINT DEFAULT 0,
            INDEX idx_account (account_number),
            INDEX idx_status (status),
            INDEX idx_timestamp (timestamp)
        )
    """)
    
    # Fraud predictions
    cursor.execute("""
        CREATE TABLE fraud_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id VARCHAR(50) NOT NULL,
            risk_score INT NOT NULL,
            is_fraud TINYINT NOT NULL,
            model_version VARCHAR(20) DEFAULT '1.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Investigations
    cursor.execute("""
        CREATE TABLE investigations (
            case_id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id VARCHAR(50) NOT NULL,
            assigned_to INT,
            status ENUM('Open', 'In_Progress', 'Resolved', 'Closed') DEFAULT 'Open',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP NULL,
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)
    
    # Seed users
    cursor.execute("""
        INSERT INTO users (id, username, email, password_hash, role)
        VALUES (1, 'admin', 'admin@mazi.com', 'hashed_admin_pass', 'admin'),
               (2, 'analyst1', 'analyst@mazi.com', 'hashed_analyst_pass', 'analyst')
    """)
    
    # Seed default settings
    cursor.execute("""
        INSERT INTO settings (user_id, operator_name, email, fraud_threshold, email_alerts, critical_alerts, weekly_reports)
        VALUES (1, 'Fraud Analyst', 'analyst@mazi.ai', 85, 1, 1, 0)
    """)
    
    # Seed realistic transactions
    accounts = [f'ACC{str(i).zfill(3)}' for i in range(1, 21)]
    locations = ['New York', 'London', 'Lagos', 'Tokyo', 'Cape Town', 'Berlin', 'Paris', 'Johannesburg', 'Durban', 'Pretoria']
    
    for i in range(50):
        acc = random.choice(accounts)
        amount = round(random.uniform(10, 25000), 2)
        is_fraud = 1 if amount > 15000 and random.random() > 0.3 else 0
        status = 'Flagged' if is_fraud else 'Safe'
        risk_score = random.randint(75, 98) if is_fraud else random.randint(5, 45)
        
        time_offset = timedelta(hours=random.randint(0, 168))
        timestamp = (datetime.now() - time_offset).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO transactions (transaction_id, account_number, amount, location, timestamp, risk_score, status, is_fraud)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (f'TXN{1000+i}', acc, amount, random.choice(locations), timestamp, risk_score, status, is_fraud))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tables created, 50 transactions seeded, settings initialized.")

if __name__ == "__main__":
    create_database()
    init_tables()
    print("✅ MySQL database fully initialized!")