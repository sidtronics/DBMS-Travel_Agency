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
        SELECT RouteID, L1.City AS Source, L2.City AS Destination
        FROM Route
        JOIN Location L1 ON Route.SourceID = L1.LocationID
        JOIN Location L2 ON Route.DestinationID = L2.LocationID
    """
    )
    routes = cur.fetchall()
    conn.close()
    return routes
