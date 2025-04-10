from database import get_connection


def create_trip_and_seats(
    route_id, bus_id, departure_time, arrival_time, trip_date, available_seats=39
):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert into Trip table
    cursor.execute(
        """
        INSERT INTO Trip (RouteID, BusID, DepartureTime, ArrivalTime, TripDate, AvailableSeats)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        (route_id, bus_id, departure_time, arrival_time, trip_date, available_seats),
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
