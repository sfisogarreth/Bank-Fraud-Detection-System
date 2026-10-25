from database.connection import get_db_connection
from werkzeug.security import generate_password_hash

def create_admin():
    username = "Sfiso Garry"
    email = "sfiso_garry@mazi.ai"
    password = "Maybe12345&"
    role = "Admin"

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, hashed_password, role)
        )
        conn.commit()
        print(f"✅ Successfully created Admin account for: {email}")
        print(f"🔑 Password: {password}")
        print(f"🛡️  Role: {role}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating account (it may already exist): {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_admin()