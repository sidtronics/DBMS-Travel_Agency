from db import get_connection


def create_trip_and_seats(
    route_id,
    bus_id,
    departure_time,
    arrival_time,
    trip_date,
    price_per_seat,
    available_seats=39,
):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert into Trip table with PricePerSeat
    cursor.execute(
        """
        INSERT INTO Trip (RouteID, BusID, DepartureTime, ArrivalTime, TripDate, AvailableSeats, PricePerSeat)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            route_id,
            bus_id,
            departure_time,
            arrival_time,
            trip_date,
            available_seats,
            price_per_seat,
        ),
    )
    trip_id = cursor.lastrowid

    # Insert 39 BookingSeat entries
    seat_data = [(trip_id, str(i), "Available") for i in range(1, available_seats + 1)]
    cursor.executemany(
        """
        INSERT INTO Seat (TripID, SeatNumber, Status)
        VALUES (%s, %s, %s)
        """,
        seat_data,
    )

    conn.commit()
    cursor.close()
    conn.close()
    return trip_id


def search_trips(source, destination, date):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT t.TripID, t.DepartureTime, t.ArrivalTime, t.AvailableSeats, t.PricePerSeat,
               b.BusNumber, b.BusType, r.Distance
        FROM Trip t
        JOIN Route r ON t.RouteID = r.RouteID
        JOIN Location l1 ON r.SourceID = l1.LocationID
        JOIN Location l2 ON r.DestinationID = l2.LocationID
        JOIN Bus b ON t.BusID = b.BusID
        WHERE l1.City = %s AND l2.City = %s AND t.TripDate = %s
    """
    cursor.execute(query, (source, destination, date))
    trips = cursor.fetchall()

    cursor.close()
    conn.close()
    return trips


def fetch_trips():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT Trip.TripID, Route.SourceID, Route.DestinationID, Bus.BusNumber,
               Trip.DepartureTime, Trip.ArrivalTime, Trip.TripDate,
               Trip.AvailableSeats, Trip.PricePerSeat
        FROM Trip
        JOIN Route ON Trip.RouteID = Route.RouteID
        JOIN Bus ON Trip.BusID = Bus.BusID
    """
    )
    trips = cur.fetchall()
    conn.close()
    return trips


def add_new_trip(route_id, bus_id, departure, arrival, date, price):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO Trip (RouteID, BusID, DepartureTime, ArrivalTime, TripDate, AvailableSeats, PricePerSeat)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (route_id, bus_id, departure, arrival, date, 39, price),
        )
        conn.commit()
    finally:
        conn.close()


def delete_trip_by_id(trip_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Trip WHERE TripID = ?", (trip_id,))
        conn.commit()
    finally:
        conn.close()


def get_trip_by_id(trip_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Trip WHERE TripID = ?", (trip_id,))
    trip = cur.fetchone()
    conn.close()
    return trip


def update_trip(
    trip_id, route_id, bus_id, departure_time, arrival_time, trip_date, price
):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE Trip
            SET RouteID = ?, BusID = ?, DepartureTime = ?, ArrivalTime = ?, TripDate = ?, PricePerSeat = ?
            WHERE TripID = ?
        """,
            (route_id, bus_id, departure_time, arrival_time, trip_date, price, trip_id),
        )
        conn.commit()
    finally:
        conn.close()
