from db import get_connection


def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Customer WHERE Username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user


def get_admin_by_username(username):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Admin WHERE Username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user


def insert_user(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Customer (FullName, Username, PasswordHash, Email, Phone, Gender, DateOfBirth)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["FullName"],
            data["Username"],
            data["PasswordHash"],
            data["Email"],
            data.get("Phone"),
            data.get("Gender"),
            data.get("DateOfBirth"),
        ),
    )
    conn.commit()
    conn.close()
