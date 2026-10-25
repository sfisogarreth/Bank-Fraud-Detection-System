-- ============================================
-- MAZI Fraud Detection System — SQLite Schema
-- ============================================

-- Drop existing tables for clean initialization
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS fraud_predictions;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

-- 1. Transactions table — matches all backend queries, ML features & XAI explanation
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
);

-- 2. Users table — for operator authentication & RBAC
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

-- 3. Settings table — for operator preferences & dynamic thresholds
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

-- 4. Fraud predictions log — for ML tracking and audit models
CREATE TABLE fraud_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    risk_score INTEGER,
    is_fraud INTEGER,
    model_version TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Audit logs — tracks operator actions (confirming fraud, marking safe, logins)
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    transaction_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. High-Speed Performance Indexes for Live Dashboard & Investigation Queries
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_number);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_risk ON transactions(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Seed test transactions with rich Explainable AI (XAI) descriptions
INSERT INTO transactions (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type, oldbalanceOrg, newbalanceOrig, explanation)
VALUES 
('TXN1001', 'ACC-7782', 12500.00, 'Johannesburg, ZA', 92, 'Flagged', 1, 'TRANSFER', 13000.00, 500.00, 'CRITICAL RISK: 96.2% account balance drain via TRANSFER | High-value anomaly (R12,500.00).'),
('TXN1002', 'ACC-9921', 450.00, 'Cape Town, ZA', 12, 'Safe', 0, 'PAYMENT', 15000.00, 14550.00, 'LOW RISK: Routine PAYMENT of R450.00 (3.0% of available balance) within normal baseline.'),
('TXN1003', 'ACC-4451', 8900.00, 'Durban, ZA', 78, 'Flagged', 1, 'CASH_OUT', 10000.00, 1100.00, 'HIGH RISK: Rapid CASH_OUT draining 89.0% of account balance.'),
('TXN1004', 'ACC-2210', 3200.00, 'Pretoria, ZA', 45, 'Safe', 0, 'PAYMENT', 22000.00, 18800.00, 'MODERATE-LOW RISK: Standard payment within normal account velocity.'),
('TXN1005', 'ACC-6677', 50000.00, 'Johannesburg, ZA', 96, 'Confirmed_Fraud', 1, 'TRANSFER', 50000.00, 0.00, 'CRITICAL FRAUD: 100% full account balance depletion (R50,000.00) via single TRANSFER.');

-- Seed default settings
INSERT INTO settings (user_id, fraud_threshold, email_alerts, critical_alerts, weekly_reports, operator_name, email)
VALUES (1, 85, 1, 1, 0, 'Fraud Analyst', 'analyst@mazi.ai');