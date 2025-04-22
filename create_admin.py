import mariadb
from db import get_connection
from utils.password import hash_password

def create_admin(username, password, email):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Hash the password before storing
        hashed_password = hash_password(password).decode("utf-8")

        # Insert admin user
        cur.execute(
            "INSERT INTO Admin (Username, PasswordHash, Email) VALUES (?, ?, ?)",
            (username, hashed_password, email)
        )

        conn.commit()
        print(f"[SUCCESS] Admin user '{username}' created successfully.")

    except mariadb.Error as e:
        print(f"[ERROR] Could not create admin: {e}")
        conn.rollback()

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_admin("admin", "p", "admin1@example.com")
