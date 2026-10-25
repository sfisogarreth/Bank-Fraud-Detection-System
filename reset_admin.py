from werkzeug.security import generate_password_hash
from database.connection import get_db_connection

def setup_admin():
    email = "sfiso_garry@mazi.ai"
    username = "Sfiso Garry"
    password = "Maybe12345&"
    role = "Admin"

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                """
                UPDATE users 
                SET password_hash = ?, role = ?, account_locked = 0, failed_attempts = 0, username = ?
                WHERE email = ?
                """,
                (hashed_pw, role, username, email)
            )
            print(f"🔄 Account already existed. Successfully RESET password for: {email}")
        else:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role, failed_attempts, account_locked)
                VALUES (?, ?, ?, ?, 0, 0)
                """,
                (username, email, hashed_pw, role)
            )
            print(f"✅ Successfully CREATED new Admin account for: {email}")

        conn.commit()
        print("\n--- LOGIN CREDENTIALS ---")
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print(f"Role:     {role}")
        print("-------------------------")

    except Exception as e:
        conn.rollback()
        print(f"❌ Database error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    setup_admin()