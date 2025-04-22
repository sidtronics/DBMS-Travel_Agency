from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.bus_model import fetch_buses
from models.trip_model import (
    fetch_trips,
    add_new_trip,
    delete_trip_by_id,
    get_trip_by_id,
    update_trip
)
from models.route_model import fetch_routes, get_all_routes


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
        trips = fetch_trips()
        routes = fetch_routes()
        buses = fetch_buses()

        return render_template(
            "admin/trips.html", trips=trips, routes=routes, buses=buses
        )

    except Exception as e:
        flash(f"Error loading trips: {str(e)}", "danger")
        return render_template("admin/trips.html", trips=[], routes=[], buses=[])


# -------------------------
# Trips - Add
# -------------------------
@admin_bp.route("/trips/add", methods=["POST"])
def add_trip():
    try:
        route_id = request.form["route_id"]
        bus_id = request.form["bus_id"]
        departure_time = request.form["departure"]
        arrival_time = request.form["arrival"]
        date = request.form["trip_date"]
        price = request.form["price"]

        departure = f"{date} {departure_time}:00"
        arrival = f"{date} {arrival_time}:00"

        add_new_trip(route_id, bus_id, departure, arrival, date, price)

        flash("Trip added successfully!", "success")
    except Exception as e:
        flash(f"Error adding trip: {str(e)}", "danger")

    return redirect(url_for("admin.manage_trips"))


# -------------------------
# Trips - Delete
# -------------------------
@admin_bp.route("/trips/delete/<int:trip_id>", methods=["POST"])
def delete_trip(trip_id):
    try:
        delete_trip_by_id(trip_id)
        flash("Trip deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting trip: {str(e)}", "danger")
    return redirect(url_for("admin.manage_trips"))


# -------------------------
# trips - edit (get+post)
# -------------------------
@admin_bp.route("/trips/edit/<int:trip_id>", methods=["GET", "POST"])
def edit_trip(trip_id):
    try:
        if request.method == "POST":
            route_id = request.form["route_id"]
            bus_id = request.form["bus_id"]
            trip_date = request.form["trip_date"]
            departure = request.form["departure"]
            arrival = request.form["arrival"]
            price = request.form["price"]

            departure_time = f"{trip_date} {departure}:00"
            arrival_time = f"{trip_date} {arrival}:00"

            update_trip(
                trip_id,
                route_id,
                bus_id,
                departure_time,
                arrival_time,
                trip_date,
                price,
            )
            flash("Trip updated successfully.", "success")
            return redirect(url_for("admin.manage_trips"))

        # GET method — load data for form
        trip = get_trip_by_id(trip_id)
        routes = get_all_routes()
        buses = fetch_buses()

        return render_template(
            "admin/edit_trip.html", trip=trip, routes=routes, buses=buses
        )

    except Exception as e:
        flash(f"Error editing trip: {str(e)}", "danger")
        return redirect(url_for("admin.manage_trips"))


# -------------------------
# routes management
# -------------------------


@admin_bp.route("/routes", methods=["get"], endpoint="manage_routes")
def manage_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "select routeid, sourceid, destinationid, distance, estimatedtime from route"
    )
    routes = cur.fetchall()
    # also fetch locations for forms
    cur.execute("select locationid, city from location")
    locations = cur.fetchall()
    conn.close()
    return render_template("admin/routes.html", routes=routes, locations=locations)


@admin_bp.route("/routes/add", methods=["post"], endpoint="add_route")
def add_route():
    data = request.form
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "insert into route (sourceid, destinationid, distance, estimatedtime) values (?, ?, ?, ?)",
            (
                data["source_id"],
                data["destination_id"],
                data["distance"],
                data["estimated_time"],
            ),
        )
        conn.commit()
        flash("route added successfully.", "success")
    except exception as e:
        flash(f"error adding route: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin.manage_routes"))


@admin_bp.route(
    "/routes/edit/<int:route_id>", methods=["get", "post"], endpoint="edit_route"
)
def edit_route(route_id):
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "post":
        data = request.form
        try:
            cur.execute(
                "update route set sourceid=?, destinationid=?, distance=?, estimatedtime=? where routeid=?",
                (
                    data["source_id"],
                    data["destination_id"],
                    data["distance"],
                    data["estimated_time"],
                    route_id,
                ),
            )
            conn.commit()
            flash("route updated.", "success")
            return redirect(url_for("admin.manage_routes"))
        except exception as e:
            flash(f"error updating route: {e}", "danger")
    # get
    cur.execute(
        "select routeid, sourceid, destinationid, distance, estimatedtime from route where routeid=?",
        (route_id,),
    )
    route = cur.fetchone()
    cur.execute("select locationid, city from location")
    locations = cur.fetchall()
    conn.close()
    return render_template("admin/edit_route.html", route=route, locations=locations)


@admin_bp.route(
    "/routes/delete/<int:route_id>", methods=["post"], endpoint="delete_route"
)
def delete_route(route_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("delete from route where routeid=?", (route_id,))
        conn.commit()
        flash("route deleted.", "success")
    except exception as e:
        flash(f"error deleting route: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin.manage_routes"))


# -------------------------
# buses management
# -------------------------
@admin_bp.route("/buses", methods=["get"], endpoint="manage_buses")
def manage_buses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("select busid, busnumber, capacity, bustype, routeid from bus")
    buses = cur.fetchall()
    cur.execute("select routeid from route")
    routes = cur.fetchall()
    conn.close()
    return render_template("admin/buses.html", buses=buses, routes=routes)


@admin_bp.route("/buses/add", methods=["post"], endpoint="add_bus")
def add_bus():
    data = request.form
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "insert into bus (busnumber, capacity, bustype, routeid) values (?, ?, ?, ?)",
            (data["bus_number"], data["capacity"], data["bus_type"], data["route_id"]),
        )
        conn.commit()
        flash("bus added.", "success")
    except exception as e:
        flash(f"error adding bus: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin.manage_buses"))


@admin_bp.route(
    "/buses/edit/<int:bus_id>", methods=["get", "post"], endpoint="edit_bus"
)
def edit_bus(bus_id):
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "post":
        data = request.form
        try:
            cur.execute(
                "update bus set busnumber=?, capacity=?, bustype=?, routeid=? where busid=?",
                (
                    data["bus_number"],
                    data["capacity"],
                    data["bus_type"],
                    data["route_id"],
                    bus_id,
                ),
            )
            conn.commit()
            flash("bus updated.", "success")
            return redirect(url_for("admin.manage_buses"))
        except exception as e:
            flash(f"error updating bus: {e}", "danger")
    cur.execute(
        "select busid, busnumber, capacity, bustype, routeid from bus where busid=?",
        (bus_id,),
    )
    bus = cur.fetchone()
    cur.execute("select routeid from route")
    routes = cur.fetchall()
    conn.close()
    return render_template("admin/edit_bus.html", bus=bus, routes=routes)


@admin_bp.route("/buses/delete/<int:bus_id>", methods=["post"], endpoint="delete_bus")
def delete_bus(bus_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("delete from bus where busid=?", (bus_id,))
        conn.commit()
        flash("bus deleted.", "success")
    except exception as e:
        flash(f"error deleting bus: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin.manage_buses"))


# -------------------------
# user management
# -------------------------
@admin_bp.route("/users", methods=["get"], endpoint="manage_users")
def manage_users():
    conn = get_connection()
    cur = conn.cursor(dictionary=true)
    cur.execute("select customerid, fullname, username, email, phone from customer")
    users = cur.fetchall()
    conn.close()
    return render_template("admin/users.html", users=users)


@admin_bp.route(
    "/users/edit/<int:user_id>", methods=["get", "post"], endpoint="edit_user"
)
def edit_user(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=true)
    if request.method == "post":
        data = request.form
        try:
            cur.execute(
                "update customer set fullname=?, email=?, phone=? where customerid=?",
                (data["fullname"], data["email"], data["phone"], user_id),
            )
            conn.commit()
            flash("user updated.", "success")
            return redirect(url_for("admin.manage_users"))
        except exception as e:
            flash(f"error updating user: {e}", "danger")
    cur.execute(
        "select customerid, fullname, username, email, phone from customer where customerid=?",
        (user_id,),
    )
    user = cur.fetchone()
    conn.close()
    return render_template("admin/edit_user.html", user=user)


@admin_bp.route("/users/delete/<int:user_id>", methods=["post"], endpoint="delete_user")
def delete_user(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("delete from customer where customerid=?", (user_id,))
        conn.commit()
        flash("user deleted.", "success")
    except exception as e:
        flash(f"error deleting user: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin.manage_users"))


# -------------------------
# booking reports
# -------------------------
@admin_bp.route("/reports/bookings", methods=["get"], endpoint="booking_reports")
def booking_reports():
    conn = get_connection()
    cur = conn.cursor(dictionary=true)
    # example: fetch total revenue per day
    cur.execute(
        "select date(bookingdate) as date, sum(totalamount) as revenue from booking group by date(bookingdate)"
    )
    reports = cur.fetchall()
    conn.close()
    return render_template("admin/booking_reports.html", reports=reports)
