from db import get_connection


def fetch_buses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT BusID, BusNumber FROM Bus")
    buses = cur.fetchall()
    conn.close()
    return buses


def get_all_buses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            Bus.BusID,
            Bus.BusNumber,
            Bus.Capacity,
            Bus.BusType,
            Bus.RouteID,
            L1.City AS Source,
            L2.City AS Destination
        FROM Bus
        JOIN Route ON Bus.RouteID = Route.RouteID
        JOIN Location L1 ON Route.SourceID = L1.LocationID
        JOIN Location L2 ON Route.DestinationID = L2.LocationID
    """)
    buses = cur.fetchall()
    conn.close()
    return buses


def add_new_bus(bus_number, capacity, bus_type, route_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Bus (BusNumber, Capacity, BusType, RouteID)
            VALUES (?, ?, ?, ?)
        """,
            (bus_number, capacity, bus_type, route_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_bus_by_id(bus_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT BusID, BusNumber, Capacity, BusType, RouteID
        FROM Bus WHERE BusID = ?
    """,
        (bus_id,),
    )
    bus = cur.fetchone()
    conn.close()
    return bus


def update_bus(bus_id, bus_number, capacity, bus_type, route_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE Bus
            SET BusNumber = ?, Capacity = ?, BusType = ?, RouteID = ?
            WHERE BusID = ?
        """,
            (bus_number, capacity, bus_type, route_id, bus_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_bus_by_id(bus_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Bus WHERE BusID = ?", (bus_id,))
        conn.commit()
    finally:
        conn.close()
