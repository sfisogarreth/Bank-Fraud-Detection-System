import os
import sys
import sqlite3
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    # Use a temporary test database
    test_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_mazi.db')
    
    # Clean up old test db
    if os.path.exists(test_db):
        os.remove(test_db)
    
    app = create_app('testing')
    app.config['DATABASE'] = test_db
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier API testing
    
    # Create test database
    with app.app_context():
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        with open(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'), 'r') as f:
            conn.executescript(f.read())
        
        # Seed test data
        conn.executemany("""
            INSERT INTO transactions (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ('TXN9991', 'ACC-TEST-1', 1000.00, 'Johannesburg', 85, 'Flagged', 1, 'TRANSFER'),
            ('TXN9992', 'ACC-TEST-2', 50.00, 'Cape Town', 10, 'Safe', 0, 'PAYMENT'),
        ])
        
        # Seed test user (password: TestPass123!)
        from werkzeug.security import generate_password_hash
        conn.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ('testuser', 'test@mazi.ai', generate_password_hash('TestPass123!', method='pbkdf2:sha256'), 'Analyst'))
        
        conn.commit()
        conn.close()
    
    yield app
    
    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()