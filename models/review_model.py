from db import get_connection
from datetime import date


def upsert_review(customer_id, booking_id, rating, comment):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if review exists
        cursor.execute(
            """
            SELECT ReviewID FROM Review
            WHERE CustomerID = %s AND BookingID = %s
        """,
            (customer_id, booking_id),
        )
        existing = cursor.fetchone()

        if existing:
            # Update
            cursor.execute(
                """
                UPDATE Review
                SET Rating = %s, Comment = %s, ReviewDate = %s
                WHERE ReviewID = %s
            """,
                (rating, comment, date.today(), existing[0]),
            )
        else:
            # Insert
            cursor.execute(
                """
                INSERT INTO Review (CustomerID, BookingID, Rating, Comment, ReviewDate)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (customer_id, booking_id, rating, comment, date.today()),
            )

        conn.commit()
    except Exception as e:
        print("Review insert/update failed:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
