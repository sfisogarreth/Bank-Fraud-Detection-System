# 🛡️ MAZI AI — Predictive Fraud Detection & Threat Command Center

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask Framework](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![C++17 Pybind11](https://img.shields.io/badge/C%2B%2B17-Pybind11-orange.svg)](https://github.com/pybind/pybind11)
[![ML Model](https://img.shields.io/badge/Scikit--Learn-Random%20Forest%20(99.9%25%20ROC--AUC)-yellow.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🚀 Executive Summary & Purpose

Modern digital banking environments face escalating threats from automated attacks, account takeovers, and high-velocity financial crime. Traditional rule-based legacy systems fail to scale effectively, generating high rates of false positives and unacceptable latency bottlenecks. 

**MAZI AI** is an enterprise-grade predictive banking fraud detection platform and operational threat command center. It continuously ingests financial transaction streams, evaluates real-time risk scores using a **Hybrid AI + C++ Engine**, and provides bank operators with **Explainable AI (XAI)** decision rationales to intercept malicious capital instantly—all packaged inside a responsive dark-mode glassmorphism web application.

---

## 👥 Project Development Team (Richfield Newtown Campus)

| Student Name | Student Number | Core Specialization & Responsibilities |
| :--- | :--- | :--- |
| **Gareth Chingwaru (Sfiso)** *(Group Leader)* | `402412340` | Machine Learning Pipeline, System Architecture, Hybrid C++ Integration & Overall Coordination (50%) |
| **Thembelele Khuzwayo** | `402412842` | Database Management, SQLite Relational Schema, Indexing & Audit Log Integrity |
| **Shelton Ngube** | `402410808` | Backend Routing, Flask Blueprints, REST APIs & C++ Binary Binding |
| **Kagiso Nyati** | `402411471` | Backend Security, Authentication Workflows, RBAC & Brute-Force Rate Limiting |
| **Sibusiso Kwinda** | `402312989` | Frontend UI Design, Glassmorphism Dashboard & Chart.js Visual Telemetry |
| **Kamuhelo Chaka** | `402309160` | Frontend Component Layout, Investigation Workflows & Responsive Styling |

**Project Supervisor:** Mr. Chulumanco Goso  
**Institution:** Richfield Graduate Institute of Technology (Faculty of Information Technology)  

---

## 🧠 How MAZI AI Works (The "Digital Bank Guard" Analogy)

Imagine a security guard standing at the door of a bank who can inspect 10,000 transactions a second:
1. **Live Ingestion:** Whenever a customer initiates a transfer, cash-out, or payment, the transaction packet hits the MAZI REST API (`/api/v1/transactions`).
2. **Hybrid Scoring:** 
   * Our **Random Forest Machine Learning model** evaluates historical fraud patterns (amount spikes, balance depletion ratios).
   * Our **C++ Fast Math engine (`fast_math.cp314`)** calculates account velocity and transaction frequency in native machine code.
3. **Explainable AI (XAI):** The system doesn't just say *"Blocked"*; it provides a breakdown of contributing risk factors (e.g., *“High account balance depletion (96.4% drained) | Proxy IP route detected”*).
4. **Action Center:** Fraud analysts review flagged cases on the dashboard, inspecting live threat heat maps and clicking **"Confirm Fraud"** or **"Mark Safe"** to record audit trails.

---

## 📂 Project Structure & File Directory Tour

```text
Bank-Fraud-Detection-System/
│
├── .vscode/                 # VS Code IntelliSense & workspace optimization settings
├── auth/                    # Role-Based Access Control (RBAC) authentication blueprint package
├── core_ml/                 # Machine learning notebooks and training pipelines
│   └── train_model.py       # Trains Random Forest on PaySim dataset and exports fraud_model.pkl
├── database/                # Relational database schema definitions
│   └── schema.sql           # SQL DDL defining transactions, users, settings, predictions, and audit logs
├── logs/                    # Runtime application and security log targets
│   └── mazi.log             # Rotating file handler capturing system events
├── models/                  # Serialized machine learning artifacts
│   ├── fraud_model.pkl      # Trained scikit-learn Random Forest classifier pipeline
│   └── model_metadata.json  # Feature names, OHE categories, and ROC-AUC metrics
├── routes/                  # Modular Flask Blueprint controllers
│   ├── analytics.py         # Statistical summaries and AI performance metrics
│   ├── api.py               # Live REST API endpoint for simulator telemetry ingestion
│   ├── audit_logs.py        # Security event tracker and search filters
│   ├── auth.py              # Login, signup, rate limiting, and password hashing logic
│   ├── dashboard.py         # Main command center metrics and live polling API
│   ├── investigations.py    # Case review, XAI lookup, and fraud resolution workflow
│   ├── reports.py           # Executive compliance report generator and CSV exporter
│   ├── settings.py          # Operator profile and dynamic threshold management
│   ├── transactions.py      # Account transaction explorer and single-tx lookup
│   └── users.py             # Admin user provisioning and account locking/unlocking
├── services/                # Business logic and computation layer
│   ├── fraud_engine.py      # ML inference wrapper and transaction feature normalizer
│   ├── prediction_service.py# Orchestrates predictions and logs to fraud_predictions table
│   ├── risk_service.py      # Smart bridge connecting Python to the C++ fast_math extension
│   ├── transaction_service.py # Database helper queries, KPI aggregations, and case loaders
│   └── xai_engine.py        # Dynamic Explainable AI feature weight and IP proxy calculator
├── static/                  # Frontend styling and client-side scripts
│   ├── css/
│   │   ├── dashboard.css    # Glassmorphism cards, shimmer loaders, and animations
│   │   └── style.css        # Global layout, sidebar navigation, and mobile responsiveness
│   └── js/
│       ├── app.js           # Live 4-second polling engine, sparklines, and toast alerts
│       └── charts.js        # Dynamic Chart.js wrappers (Risk Gauge, Trends, Attack Vectors)
├── templates/               # Jinja2 HTML presentation views
│   ├── base.html            # Master layout template with sidebar and flash notifications
│   ├── dashboard.html       # Real-time threat command center and interactive telemetry
│   ├── analytics.html       # AI accuracy radar charts and risk distribution bars
│   ├── audit_logs.html      # Searchable security event log table
│   ├── investigation.html   # Case detail view featuring Explainable AI (XAI) feature breakdown
│   ├── investigation_logs.html # Comprehensive queue of flagged risk interceptions
│   ├── login.html           # Secure operator authentication portal
│   ├── reports.html         # Executive summary reports with print/PDF export
│   ├── settings.html        # AI threshold slider and notification preferences
│   ├── signup.html          # Operator clearance request form with live password validator
│   ├── transactions.html    # Filterable ledger of all processed transactions
│   ├── users.html           # Admin directory for managing operator roles and account locking
│   └── coming_soon.html     # Graceful fallback view for development modules
│
├── .env                     # Local environment configuration secrets
├── .env.example             # Configuration template for deployment
├── app.py                   # Main Flask application factory and server entry point
├── config.py                # Environment parser and production/development configuration classes
├── create_admin.py          # Standalone helper script for admin provisioning
├── create_db.py             # Standalone helper script for SQLite initialization
├── fast_math.cpp            # C++17 Pybind11 source code for high-speed velocity math
├── init_db.py               # Master database setup, schema builder, and seed data loader
├── mazi.db                  # Active SQLite relational database store
├── real_data.py             # Kaggle PaySim dataset importer for testing live loads
├── requirements.txt         # Complete Python package dependency manifest
├── reset_admin.py           # Utility script to reset admin credentials in mazi.db
├── setup.py                 # C++ extension build script for compiling fast_math.pyd
├── simulator.py             # Background script simulating live multi-region banking traffic
├── test_app.py              # Automated unit and integration test suite (7 comprehensive tests)
└── test_cpp.py              # Diagnostic verification script for C++ fast_math binding
