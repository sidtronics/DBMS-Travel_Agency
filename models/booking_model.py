from db import get_connection
from datetime import datetime


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


def create_booking_and_payment(
    customer_id, trip_id, seat_numbers, amount, payment_method
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert into Booking table
        cursor.execute(
            """
            INSERT INTO Booking (CustomerID, TripID, BookingDate, TotalSeats, TotalAmount)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (customer_id, trip_id, datetime.now(), len(seat_numbers), amount),
        )
        booking_id = cursor.lastrowid

        # Mark the seats with BookingID and Status = 'Booked'
        format_strings = ",".join(["%s"] * len(seat_numbers))
        cursor.execute(
            f"""
            UPDATE Seat
            SET Status = 'Booked'
            WHERE TripID = %s AND SeatNumber IN ({format_strings}) AND Status = 'Available'
        """,
            [trip_id] + seat_numbers,
        )

        # Insert into Payment table
        cursor.execute(
            """
            INSERT INTO Payment (BookingID, Amount, PaymentMethod, PaymentDate)
            VALUES (%s, %s, %s, %s)
        """,
            (booking_id, amount, payment_method, datetime.now()),
        )

        conn.commit()
        return True
    except Exception as e:
        print("Error in payment transaction:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
