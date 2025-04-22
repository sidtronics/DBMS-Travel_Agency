from db import get_connection


def fetch_buses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT BusID, BusNumber FROM Bus")
    buses = cur.fetchall()
    conn.close()
    return buses
