from flask import render_template, session, redirect, url_for, flash, request
import mariadb
from db import get_connection
from . import admin_bp

# Admin-only check
def is_admin():
    return session.get("user", {}).get("admin") == "yes"

@admin_bp.before_request
def restrict_to_admins():
    if not is_admin():
        flash("Admins only area. Please log in as an admin.", "danger")
        return redirect(url_for("auth.login"))

# -------------------------
# Dashboard
# -------------------------
@admin_bp.route("/")
def index():
    return render_template("admin/admin_dashboard.html")

# -------------------------
# Trips - View
# -------------------------
@admin_bp.route("/trips", methods=["GET", "POST"], endpoint="manage_trips")
def manage_trips():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Fetch trips with joins
        cur.execute("""
            SELECT Trip.TripID, Route.SourceID, Route.DestinationID, Bus.BusNumber,
                   Trip.DepartureTime, Trip.ArrivalTime, Trip.TripDate,
                   Trip.AvailableSeats, Trip.PricePerSeat
            FROM Trip
            JOIN Route ON Trip.RouteID = Route.RouteID
            JOIN Bus ON Trip.BusID = Bus.BusID
        """)
        trips = cur.fetchall()

        # Fetch routes for dropdowns
        cur.execute("""
            SELECT RouteID, L1.City AS Source, L2.City AS Destination
            FROM Route
            JOIN Location L1 ON Route.SourceID = L1.LocationID
            JOIN Location L2 ON Route.DestinationID = L2.LocationID
        """)
        routes = cur.fetchall()

        # Fetch buses
        cur.execute("SELECT BusID, BusNumber FROM Bus")
        buses = cur.fetchall()

        return render_template("admin/trips.html", trips=trips, routes=routes, buses=buses)

    except Exception as e:
        flash(f"Error loading trips: {str(e)}", "danger")
        return render_template("admin/trips.html", trips=[], routes=[], buses=[])

    finally:
        if conn:
            conn.close()

# -------------------------
# Trips - Add
# -------------------------
@admin_bp.route("/trips/add", methods=["POST"])
def add_trip():
    try:
        conn = get_connection()
        cur = conn.cursor()

        route_id = request.form["route_id"]
        bus_id = request.form["bus_id"]
        departure = request.form["departure"]
        arrival = request.form["arrival"]
        date = request.form["trip_date"]
        price = request.form["price"]

        cur.execute("""
            INSERT INTO Trip (RouteID, BusID, DepartureTime, ArrivalTime, TripDate, AvailableSeats, PricePerSeat)
            VALUES (%s, %s, %s, %s, %s, %s, 39)
        """, (route_id, bus_id, departure, arrival, date, price))

        conn.commit()
        flash("Trip added successfully!", "success")
    except Exception as e:
        flash(f"Error adding trip: {str(e)}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("admin.manage_trips"))

# -------------------------
# Trips - Delete
# -------------------------
@admin_bp.route("/trips/delete/<int:trip_id>", methods=["POST"])
def delete_trip(trip_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Trip WHERE TripID=?", (trip_id,))
        conn.commit()
        flash("Trip deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting trip: {str(e)}", "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for("admin.manage_trips"))

# -------------------------
# Trips - Edit (GET+POST)
# -------------------------
@admin_bp.route("/trips/edit/<int:trip_id>", methods=["GET", "POST"])
def edit_trip(trip_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":
            # Update
            route_id = request.form["route_id"]
            bus_id = request.form["bus_id"]
            departure = request.form["departure"]
            arrival = request.form["arrival"]
            date = request.form["trip_date"]
            price = request.form["price"]

            cur.execute("""
                UPDATE Trip SET RouteID=?, BusID=?, DepartureTime=?, ArrivalTime=?, TripDate=?, PricePerSeat=?
                WHERE TripID=?
            """, (route_id, bus_id, departure, arrival, date, price, trip_id))
            conn.commit()
            flash("Trip updated successfully.", "success")
            return redirect(url_for("admin.manage_trips"))

        # GET - fetch trip info
        cur.execute("SELECT * FROM Trip WHERE TripID=?", (trip_id,))
        trip = cur.fetchone()

        cur.execute("""
            SELECT RouteID, L1.City AS Source, L2.City AS Destination
            FROM Route
            JOIN Location L1 ON Route.SourceID = L1.LocationID
            JOIN Location L2 ON Route.DestinationID = L2.LocationID
        """)
        routes = cur.fetchall()

        cur.execute("SELECT BusID, BusNumber FROM Bus")
        buses = cur.fetchall()

        return render_template("admin/edit_trip.html", trip=trip, routes=routes, buses=buses)

    except Exception as e:
        flash(f"Error editing trip: {str(e)}", "danger")
        return redirect(url_for("admin.manage_trips"))

    finally:
        if conn:
            conn.close()

# -------------------------
# Routes Management
# -------------------------
@admin_bp.route("/routes", methods=["GET"], endpoint="manage_routes")
def manage_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT RouteID, SourceID, DestinationID, Distance, EstimatedTime FROM Route")
    routes = cur.fetchall()
    # Also fetch locations for forms
    cur.execute("SELECT LocationID, City FROM Location")
    locations = cur.fetchall()
    conn.close()
    return render_template("admin/routes.html", routes=routes, locations=locations)

@admin_bp.route("/routes/add", methods=["POST"], endpoint="add_route")
def add_route():
    data = request.form
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO Route (SourceID, DestinationID, Distance, EstimatedTime) VALUES (?, ?, ?, ?)",
            (data['source_id'], data['destination_id'], data['distance'], data['estimated_time'])
        )
        conn.commit()
        flash("Route added successfully.", "success")
    except Exception as e:
        flash(f"Error adding route: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin.manage_routes'))

@admin_bp.route("/routes/edit/<int:route_id>", methods=["GET", "POST"], endpoint="edit_route")
def edit_route(route_id):
    conn = get_connection(); cur = conn.cursor()
    if request.method == "POST":
        data = request.form
        try:
            cur.execute(
                "UPDATE Route SET SourceID=?, DestinationID=?, Distance=?, EstimatedTime=? WHERE RouteID=?",
                (data['source_id'], data['destination_id'], data['distance'], data['estimated_time'], route_id)
            )
            conn.commit(); flash("Route updated.", "success")
            return redirect(url_for('admin.manage_routes'))
        except Exception as e:
            flash(f"Error updating route: {e}", "danger")
    # GET
    cur.execute("SELECT RouteID, SourceID, DestinationID, Distance, EstimatedTime FROM Route WHERE RouteID=?", (route_id,))
    route = cur.fetchone()
    cur.execute("SELECT LocationID, City FROM Location"); locations = cur.fetchall()
    conn.close()
    return render_template("admin/edit_route.html", route=route, locations=locations)

@admin_bp.route("/routes/delete/<int:route_id>", methods=["POST"], endpoint="delete_route")
def delete_route(route_id):
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Route WHERE RouteID=?", (route_id,))
        conn.commit(); flash("Route deleted.", "success")
    except Exception as e:
        flash(f"Error deleting route: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin.manage_routes'))

# -------------------------
# Buses Management
# -------------------------
@admin_bp.route("/buses", methods=["GET"], endpoint="manage_buses")
def manage_buses():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT BusID, BusNumber, Capacity, BusType, RouteID FROM Bus")
    buses = cur.fetchall()
    cur.execute("SELECT RouteID FROM Route"); routes = cur.fetchall()
    conn.close()
    return render_template("admin/buses.html", buses=buses, routes=routes)

@admin_bp.route("/buses/add", methods=["POST"], endpoint="add_bus")
def add_bus():
    data = request.form
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO Bus (BusNumber, Capacity, BusType, RouteID) VALUES (?, ?, ?, ?)",
            (data['bus_number'], data['capacity'], data['bus_type'], data['route_id'])
        )
        conn.commit(); flash("Bus added.", "success")
    except Exception as e:
        flash(f"Error adding bus: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin.manage_buses'))

@admin_bp.route("/buses/edit/<int:bus_id>", methods=["GET", "POST"], endpoint="edit_bus")
def edit_bus(bus_id):
    conn = get_connection(); cur = conn.cursor()
    if request.method == 'POST':
        data = request.form
        try:
            cur.execute(
                "UPDATE Bus SET BusNumber=?, Capacity=?, BusType=?, RouteID=? WHERE BusID=?",
                (data['bus_number'], data['capacity'], data['bus_type'], data['route_id'], bus_id)
            )
            conn.commit(); flash("Bus updated.", "success")
            return redirect(url_for('admin.manage_buses'))
        except Exception as e:
            flash(f"Error updating bus: {e}", "danger")
    cur.execute("SELECT BusID, BusNumber, Capacity, BusType, RouteID FROM Bus WHERE BusID=?", (bus_id,))
    bus = cur.fetchone(); cur.execute("SELECT RouteID FROM Route"); routes = cur.fetchall()
    conn.close()
    return render_template("admin/edit_bus.html", bus=bus, routes=routes)

@admin_bp.route("/buses/delete/<int:bus_id>", methods=["POST"], endpoint="delete_bus")
def delete_bus(bus_id):
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Bus WHERE BusID=?", (bus_id,))
        conn.commit(); flash("Bus deleted.", "success")
    except Exception as e:
        flash(f"Error deleting bus: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin.manage_buses'))

# -------------------------
# User Management
# -------------------------
@admin_bp.route("/users", methods=["GET"], endpoint="manage_users")
def manage_users():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT CustomerID, FullName, Username, Email, Phone FROM Customer")
    users = cur.fetchall(); conn.close()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"], endpoint="edit_user")
def edit_user(user_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.form
        try:
            cur.execute(
                "UPDATE Customer SET FullName=?, Email=?, Phone=? WHERE CustomerID=?",
                (data['fullname'], data['email'], data['phone'], user_id)
            )
            conn.commit(); flash("User updated.", "success")
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            flash(f"Error updating user: {e}", "danger")
    cur.execute("SELECT CustomerID, FullName, Username, Email, Phone FROM Customer WHERE CustomerID=?", (user_id,))
    user = cur.fetchone(); conn.close()
    return render_template("admin/edit_user.html", user=user)

@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"], endpoint="delete_user")
def delete_user(user_id):
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Customer WHERE CustomerID=?", (user_id,))
        conn.commit(); flash("User deleted.", "success")
    except Exception as e:
        flash(f"Error deleting user: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin.manage_users'))

# -------------------------
# Booking Reports
# -------------------------
@admin_bp.route("/reports/bookings", methods=["GET"], endpoint="booking_reports")
def booking_reports():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    # Example: fetch total revenue per day
    cur.execute(
        "SELECT DATE(BookingDate) AS date, SUM(TotalAmount) AS revenue FROM Booking GROUP BY DATE(BookingDate)"
    )
    reports = cur.fetchall(); conn.close()
    return render_template("admin/booking_reports.html", reports=reports)
