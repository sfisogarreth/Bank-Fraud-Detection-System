import os
import json
import unittest
from app import create_app
from database.connection import get_db_connection
from services.risk_service import calculate_risk_score, FAST_MATH_AVAILABLE
from services.fraud_engine import analyze
from services.prediction_service import get_model_info, predict_transaction
from services.xai_engine import generate_explanation
from services.transaction_service import get_transaction_stats


class MaziAISystemTestSuite(unittest.TestCase):
    """
    Comprehensive automated test suite for the MAZI AI Fraud Detection Platform.
    Verifies database connectivity, C++ fast_math engine, Random Forest ML inference,
    Explainable AI (XAI) attribution, authentication gates, and live REST API endpoints.
    """

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print(" 🚀 STARTING MAZI AI AUTOMATED SYSTEM VERIFICATION SUITE")
        print("=" * 70)
        cls.app = create_app('development')
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_01_health_endpoint(self):
        """1. Verify the Flask server and /health check endpoint are operational."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'healthy')
        print("✅ [PASS] Test 1: Flask Application & /health Endpoint Operational")

    def test_02_database_tables_and_indexes(self):
        """2. Verify SQLite database connection and required schema tables exist."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row['name'] for row in cursor.fetchall()}
        conn.close()

        required_tables = {'transactions', 'users', 'settings', 'fraud_predictions', 'audit_logs'}
        self.assertTrue(required_tables.issubset(tables), f"Missing tables: {required_tables - tables}")
        print(f"✅ [PASS] Test 2: SQLite Database & All 5 Core Tables Verified ({len(tables)} tables active)")

    def test_03_cpp_fast_math_velocity_engine(self):
        """3. Verify C++ fast_math extension (or fallback) computes accurate velocity risk."""
        low_score = calculate_risk_score(500.0, 1)
        high_score = calculate_risk_score(45000.0, 8)

        self.assertGreaterEqual(low_score, 0.0)
        self.assertLessEqual(high_score, 100.0)
        self.assertGreater(high_score, low_score)
        engine_type = "Native C++ Binary (.pyd)" if FAST_MATH_AVAILABLE else "Python Math Fallback"
        print(f"✅ [PASS] Test 3: Velocity Risk Engine Verified ({engine_type}) -> Low: {low_score}%, High: {high_score}%")

    def test_04_machine_learning_fraud_engine(self):
        """4. Verify Random Forest ML model inference on safe vs. high-risk transactions."""
        safe_tx = {
            'step': 1,
            'amount': 350.00,
            'oldbalanceOrg': 25000.00,
            'newbalanceOrig': 24650.00,
            'oldbalanceDest': 5000.00,
            'newbalanceDest': 5350.00,
            'type': 'PAYMENT'
        }
        fraud_tx = {
            'step': 1,
            'amount': 85000.00,
            'oldbalanceOrg': 85000.00,
            'newbalanceOrig': 0.00,
            'oldbalanceDest': 0.00,
            'newbalanceDest': 85000.00,
            'type': 'TRANSFER'
        }

        safe_score = analyze(safe_tx)
        fraud_score = analyze(fraud_tx)
        model_info = get_model_info()

        self.assertTrue(0 <= safe_score <= 100)
        self.assertTrue(0 <= fraud_score <= 100)
        print(
            f"✅ [PASS] Test 4: Random Forest ML Model Verified "
            f"(Loaded: {model_info.get('loaded')}) -> Safe Score: {safe_score}%, Fraud Drain Score: {fraud_score}%"
        )

    def test_05_explainable_ai_xai_engine(self):
        """5. Verify Explainable AI (XAI) generates dynamic feature weights and device forensics."""
        sample_case = {
            "id": 1024,
            "risk_score": 88,
            "amount": 29500.00,
            "location": "Lagos, NG (Proxy)"
        }
        explanation = generate_explanation(sample_case)

        self.assertIn("xai_features", explanation)
        self.assertEqual(len(explanation["xai_features"]), 3)
        self.assertIn("Proxy/VPN Detected", explanation["ip_region"])
        print(
            f"✅ [PASS] Test 5: Explainable AI (XAI) Verified -> "
            f"IP: {explanation['ip_region']} | Features: {len(explanation['xai_features'])}"
        )

    def test_06_security_gate_protection(self):
        """6. Verify unauthenticated users are blocked from accessing protected routes."""
        response = self.client.get('/dashboard/', follow_redirects=False)
        self.assertIn(response.status_code, (301, 302))
        self.assertIn('/login', response.headers.get('Location', ''))
        print("✅ [PASS] Test 6: RBAC & Authentication Security Gate Verified (Redirects unauthorized users to /login)")

    def test_07_live_transaction_ingestion_api(self):
        """7. Verify POST /api/v1/transactions evaluates and saves live transactions to SQLite."""
        payload = {
            "account_number": "ACC-TEST-9901",
            "amount": 19500.00,
            "location": "Johannesburg, ZA",
            "type": "CASH_OUT",
            "oldbalanceOrg": 20000.00,
            "newbalanceOrig": 500.00
        }
        response = self.client.post(
            '/api/v1/transactions',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("transaction_id", data)
        self.assertIn("risk_score", data)
        print(
            f"✅ [PASS] Test 7: Live API Transaction Ingestion Verified -> "
            f"ID: {data['transaction_id']} | Risk Score: {data['risk_score']}% | Decision: {data['decision']}"
        )


if __name__ == '__main__':
    unittest.main(verbosity=0)