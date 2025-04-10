from db import get_connection


def get_customer_bookings(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            b.BookingID,
            t.TripDate,
            t.DepartureTime,
            t.ArrivalTime,
            bs.BusNumber,
            r.RouteID,
            l1.City AS Source,
            l2.City AS Destination,
            b.TotalSeats,
            b.TotalAmount,
        FROM Booking b
        JOIN Trip t ON b.TripID = t.TripID
        JOIN Bus bs ON t.BusID = bs.BusID
        JOIN Route r ON t.RouteID = r.RouteID
        JOIN Location l1 ON r.SourceID = l1.LocationID
        JOIN Location l2 ON r.DestinationID = l2.LocationID
        WHERE b.CustomerID = %s
        ORDER BY b.BookingDate DESC
    """
    cursor.execute(query, (customer_id,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()
    return bookings


def search_trips(source, destination, date):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT t.TripID, t.DepartureTime, t.ArrivalTime, t.AvailableSeats,
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


def get_available_seats(trip_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT SeatID, SeatNumber
        FROM Seat
        WHERE TripID = %s AND Status = 'Available'
        ORDER BY CAST(SeatNumber AS UNSIGNED)
    """,
        (trip_id,),
    )

    seats = cursor.fetchall()
    cursor.close()
    conn.close()
    return seats


def book_selected_seats(trip_id, seat_numbers):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        format_strings = ",".join(["%s"] * len(seat_numbers))
        query = f"""
            UPDATE Seat
            SET Status = 'Booked'
            WHERE TripID = %s AND SeatNumber IN ({format_strings}) AND Status = 'Available'
        """
        values = [trip_id] + seat_numbers
        cursor.execute(query, values)

        # Ensure all requested seats were updated
        if cursor.rowcount != len(seat_numbers):
            conn.rollback()
            return False

        conn.commit()
        return True
    except Exception as e:
        print("Error booking seats:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
