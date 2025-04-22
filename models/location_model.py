from db import get_connection


def get_all_locations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT LocationID, City, State, Pincode FROM Location")
    locations = cur.fetchall()
    conn.close()
    return locations


def add_new_location(city, state, pincode):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Location (City, State, Pincode)
            VALUES (?, ?, ?)
        """,
            (city, state, pincode),
        )
        conn.commit()
    finally:
        conn.close()


def get_location_by_id(location_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT LocationID, City, State, Pincode
        FROM Location
        WHERE LocationID = ?
    """,
        (location_id,),
    )
    location = cur.fetchone()
    conn.close()
    return location


def update_location(location_id, city, state, pincode):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE Location
            SET City = ?, State = ?, Pincode = ?
            WHERE LocationID = ?
        """,
            (city, state, pincode, location_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_location_by_id(location_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Location WHERE LocationID = ?", (location_id,))
        conn.commit()
    finally:
        conn.close()
