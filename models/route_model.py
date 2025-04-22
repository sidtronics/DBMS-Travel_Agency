from db import get_connection


def fetch_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT RouteID, L1.City AS Source, L2.City AS Destination
        FROM Route
        JOIN Location L1 ON Route.SourceID = L1.LocationID
        JOIN Location L2 ON Route.DestinationID = L2.LocationID
    """
    )
    routes = cur.fetchall()
    conn.close()
    return routes


def get_all_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT RouteID, L1.City AS Source, L2.City AS Destination, Distance, EstimatedTime
        FROM Route
        JOIN Location L1 ON Route.SourceID = L1.LocationID
        JOIN Location L2 ON Route.DestinationID = L2.LocationID
    """
    )
    routes = cur.fetchall()
    conn.close()
    return routes


def add_new_route(source_id, destination_id, distance, estimated_time):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Route (SourceID, DestinationID, Distance, EstimatedTime)
            VALUES (?, ?, ?, ?)
        """,
            (source_id, destination_id, distance, estimated_time),
        )
        conn.commit()
    finally:
        conn.close()


def get_route_by_id(route_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT RouteID, SourceID, DestinationID, Distance, EstimatedTime
        FROM Route
        WHERE RouteID = ?
    """,
        (route_id,),
    )
    route = cur.fetchone()
    conn.close()
    return route


def update_route(route_id, source_id, destination_id, distance, estimated_time):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE Route
            SET SourceID = ?, DestinationID = ?, Distance = ?, EstimatedTime = ?
            WHERE RouteID = ?
        """,
            (source_id, destination_id, distance, estimated_time, route_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_route_by_id(route_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Route WHERE RouteID = ?", (route_id,))
        conn.commit()
    finally:
        conn.close()
