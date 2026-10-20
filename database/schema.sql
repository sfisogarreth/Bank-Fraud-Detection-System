-- ============================================
-- MAZI Fraud Detection System — SQLite Schema
-- ============================================

-- Drop existing tables for clean init (optional, remove if you want to keep data)
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS fraud_predictions;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

-- 1. Transactions table — matches all backend queries
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
);

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

);

-- 3. Settings table — for operator preferences
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    fraud_threshold INTEGER DEFAULT 85,
    email_alerts INTEGER DEFAULT 1,
    critical_alerts INTEGER DEFAULT 1,
    weekly_reports INTEGER DEFAULT 0,
    operator_name TEXT DEFAULT 'Fraud Analyst',
    email TEXT DEFAULT 'analyst@mazi.ai'
);

-- 4. Fraud predictions log — for ML tracking
CREATE TABLE fraud_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    risk_score INTEGER,
    is_fraud INTEGER,
    model_version TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Audit logs — tracks who confirmed/marked safe
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    transaction_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed data for testing
INSERT INTO transactions (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type)
VALUES 
('TXN1001', 'ACC-7782', 12500.00, 'Johannesburg', 92, 'Flagged', 1, 'TRANSFER'),
('TXN1002', 'ACC-9921', 450.00, 'Cape Town', 12, 'Safe', 0, 'PAYMENT'),
('TXN1003', 'ACC-4451', 8900.00, 'Durban', 78, 'Flagged', 0, 'CASH_OUT'),
('TXN1004', 'ACC-2210', 3200.00, 'Pretoria', 45, 'Safe', 0, 'PAYMENT'),
('TXN1005', 'ACC-6677', 50000.00, 'Johannesburg', 96, 'Confirmed_Fraud', 1, 'TRANSFER');

-- Seed default admin user (password: admin123 — change immediately!)
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@mazi.ai', 'pbkdf2:sha256:600000$dummyhash$changeme', 'Manager');

-- Seed default settings
INSERT INTO settings (user_id, fraud_threshold, email_alerts, critical_alerts, weekly_reports, operator_name, email)
VALUES (1, 85, 1, 1, 0, 'Fraud Analyst', 'analyst@mazi.ai');