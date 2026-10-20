from database.connection import get_db_connection


def test_database_connection(app):
    """Database should be queryable."""
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        result = cursor.fetchone()
        assert result['count'] >= 2  # Our seeded data
        cursor.close()
        conn.close()


def test_users_table_exists(app):
    """Users table should have our test user."""
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", ('test@mazi.ai',))
        user = cursor.fetchone()
        assert user is not None
        assert user['username'] == 'testuser'
        assert user['role'] == 'Analyst'
        cursor.close()
        conn.close()