from db import get_connection


def get_all_locations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT LocationID, City FROM Location")
    locations = cur.fetchall()
    conn.close()
    return locations
