from db import get_connection


def get_daily_booking_revenue():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT DATE(BookingDate) AS date, SUM(TotalAmount) AS revenue
        FROM Booking
        GROUP BY DATE(BookingDate)
        ORDER BY date DESC
    """
    )
    reports = cur.fetchall()
    conn.close()
    return reports
