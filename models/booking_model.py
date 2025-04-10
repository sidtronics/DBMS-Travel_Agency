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


def create_booking_and_payment(customer_id, trip_id, seat_numbers, payment_method):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Fetch PricePerSeat from Trip
        cursor.execute("SELECT PricePerSeat FROM Trip WHERE TripID = %s", (trip_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception("Trip not found.")
        price_per_seat = result[0]

        total_seats = len(seat_numbers)
        total_amount = total_seats * price_per_seat

        # Insert into Booking table
        cursor.execute(
            """
            INSERT INTO Booking (CustomerID, TripID, BookingDate, TotalSeats, TotalAmount)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (customer_id, trip_id, datetime.now(), total_seats, total_amount),
        )
        booking_id = cursor.lastrowid

        # Mark the seats as Booked
        format_strings = ",".join(["%s"] * total_seats)
        cursor.execute(
            f"""
            UPDATE Seat
            SET Status = 'Booked', BookingID = %s
            WHERE TripID = %s AND SeatNumber IN ({format_strings}) AND Status = 'Available'
            """,
            [booking_id, trip_id] + seat_numbers,
        )
        if cursor.rowcount != total_seats:
            raise Exception("Some seats are already booked.")

        # Insert into Payment table
        cursor.execute(
            """
            INSERT INTO Payment (BookingID, Amount, PaymentMethod, PaymentDate)
            VALUES (%s, %s, %s, %s)
            """,
            (booking_id, total_amount, payment_method, datetime.now()),
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


def get_booking_with_seats_and_review(customer_id, booking_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Booking details
        cursor.execute(
            """
            SELECT b.BookingID, b.BookingDate, b.TotalSeats, b.TotalAmount,
                   t.TripDate, t.DepartureTime, t.ArrivalTime,
                   r.RouteID, r.SourceID, r.DestinationID
            FROM Booking b
            JOIN Trip t ON b.TripID = t.TripID
            JOIN Route r ON t.RouteID = r.RouteID
            WHERE b.BookingID = %s AND b.CustomerID = %s
        """,
            (booking_id, customer_id),
        )
        booking = cursor.fetchone()
        if not booking:
            return None, None, None

        # Seats
        cursor.execute(
            """
            SELECT SeatNumber FROM Seat
            WHERE BookingID = %s
        """,
            (booking_id,),
        )
        seats = [row["SeatNumber"] for row in cursor.fetchall()]

        # Review (optional)
        cursor.execute(
            """
            SELECT Rating, Comment, ReviewDate
            FROM Review
            WHERE BookingID = %s AND CustomerID = %s
        """,
            (booking_id, customer_id),
        )
        review = cursor.fetchone()

        return booking, seats, review
    finally:
        cursor.close()
        conn.close()
