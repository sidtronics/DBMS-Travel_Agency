import mariadb
from datetime import datetime

from db import get_connection


def seed_data():
    try:
        conn = get_connection()
        cur = conn.cursor()

        print("[SEED]: Seeding sample data...")

        # 1. Locations
        locations = [
            ("Mumbai", "Maharashtra", "400001"),
            ("Pune", "Maharashtra", "411001"),
            ("Delhi", "Delhi", "110001"),
            ("Agra", "Uttar Pradesh", "282001"),
            ("Chennai", "Tamil Nadu", "600001"),
            ("Bangalore", "Karnataka", "560001"),
        ]
        cur.executemany("INSERT INTO Location (City, State, Pincode) VALUES (?, ?, ?)", locations)

        # Get LocationIDs
        cur.execute("SELECT City, LocationID FROM Location")
        loc_map = {city: loc_id for city, loc_id in cur.fetchall()}

        # 2. Routes
        routes = [
            (loc_map["Mumbai"], loc_map["Pune"], 150.0, "3 hours"),
            (loc_map["Delhi"], loc_map["Agra"], 220.0, "4 hours"),
            (loc_map["Mumbai"], loc_map["Agra"], 1200.0, "16 hours"),
            (loc_map["Delhi"], loc_map["Pune"], 1500.0, "18 hours"),
        ]
        cur.executemany(
            "INSERT INTO Route (SourceID, DestinationID, Distance, EstimatedTime) VALUES (?, ?, ?, ?)", routes
        )

        # 3. Buses
        buses = [
            ("MH01AB1234", 40, "AC", 1),
            ("DL05XY6789", 35, "Non-AC", 2),
            ("UP32JK1122", 45, "AC", 3),
            ("MH12ZZ5566", 30, "Non-AC", 4),
        ]
        cur.executemany(
            "INSERT INTO Bus (BusNumber, Capacity, BusType, RouteID) VALUES (?, ?, ?, ?)", buses
        )

        # 4. Customers
        customers = [
            ("Alice Sharma", "alice123", "hashedpass1", "alice@example.com", "9876543210", "Female", "1995-05-10"),
            ("Bob Mehta", "bobm", "hashedpass2", "bob@example.com", "9123456789", "Male", "1992-03-20"),
        ]
        cur.executemany(
            "INSERT INTO Customer (FullName, Username, PasswordHash, Email, Phone, Gender, DateOfBirth) VALUES (?, ?, ?, ?, ?, ?, ?)",
            customers,
        )

        # 5. Admin
        cur.execute("INSERT INTO Admin (Username, PasswordHash, Email) VALUES (?, ?, ?)", ("admin1", "adminpass", "admin@example.com"))

        # 6. Employees
        employees = [
            ("Ravi Kumar", "Driver", "9000011111", "123 Main St", "2022-01-01"),
            ("Sita Das", "Conductor", "9000022222", "456 Second St", "2023-03-10"),
            ("Arun Dev", "Cleaner", "9000033333", "789 Third St", "2024-06-15"),
        ]
        cur.executemany(
            "INSERT INTO Employee (Name, Role, Phone, Address, DateOfJoining) VALUES (?, ?, ?, ?, ?)",
            employees,
        )

        # 7. Trips + Seats
        trips = [
            (1, 1, "2025-04-15 09:00:00", "2025-04-15 12:00:00", "2025-04-15", 450.0),
            (2, 2, "2025-04-16 08:30:00", "2025-04-16 12:30:00", "2025-04-16", 600.0),
            (3, 3, "2025-04-17 07:00:00", "2025-04-17 23:00:00", "2025-04-17", 1200.0),
            (4, 4, "2025-04-18 06:00:00", "2025-04-18 23:30:00", "2025-04-18", 1100.0),
            (5, 5, "2025-04-15 06:00:00", "2025-04-15 23:30:00", "2025-04-15", 1100.0),
        ]

        for route_id, bus_id, dep, arr, date, price in trips:
            cur.execute(
                """
                INSERT INTO Trip (RouteID, BusID, DepartureTime, ArrivalTime, TripDate, AvailableSeats, PricePerSeat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (route_id, bus_id, dep, arr, date, 39, price),
            )
            trip_id = cur.lastrowid

            seats = [(trip_id, f"{chr(65 + i // 4)}{i % 4 + 1}", "Available", None) for i in range(39)]
            cur.executemany("INSERT INTO Seat (TripID, SeatNumber, Status, BookingID) VALUES (?, ?, ?, ?)", seats)

        # 8. Bookings
        cur.execute("INSERT INTO Booking (CustomerID, TripID, BookingDate, TotalSeats, TotalAmount) VALUES (?, ?, ?, ?, ?)",
                    (1, 3, datetime.now(), 2, 2400.00))
        booking1_id = cur.lastrowid

        cur.execute("INSERT INTO Booking (CustomerID, TripID, BookingDate, TotalSeats, TotalAmount) VALUES (?, ?, ?, ?, ?)",
                    (2, 2, datetime.now(), 1, 600.00))
        booking2_id = cur.lastrowid

        # 9. Seat Status Update
        cur.execute("UPDATE Seat SET Status='Booked', BookingID=? WHERE TripID=3 AND SeatNumber IN ('A1', 'A2')", (booking1_id,))
        cur.execute("UPDATE Seat SET Status='Booked', BookingID=? WHERE TripID=2 AND SeatNumber='A1'", (booking2_id,))

        # 10. Payments
        cur.executemany(
            "INSERT INTO Payment (BookingID, Amount, PaymentMethod, PaymentDate) VALUES (?, ?, ?, ?)",
            [
                (booking1_id, 2400.00, "Card", datetime.now()),
                (booking2_id, 600.00, "UPI", datetime.now()),
            ]
        )

        # 11. Review
        cur.execute(
            "INSERT INTO Review (CustomerID, BookingID, Rating, Comment, ReviewDate) VALUES (?, ?, ?, ?, ?)",
            (1, booking1_id, 4.5, "Comfortable journey and clean bus.", datetime.now())
        )

        conn.commit()
        print("[SEED]: Data inserted successfully.")

    except mariadb.Error as e:
        print(f"[SEED ERROR]: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    seed_data()
