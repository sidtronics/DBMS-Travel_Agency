from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.report_model import get_daily_booking_revenue
from models.bus_model import (
    get_all_buses,
    add_new_bus,
    get_bus_by_id,
    update_bus,
    delete_bus_by_id,
    fetch_buses,
)
from models.route_model import (
    add_new_route,
    get_all_routes,
    get_route_by_id,
    fetch_routes,
    update_route,
    delete_route_by_id,
)
from models.trip_model import (
    fetch_trips,
    add_new_trip,
    delete_trip_by_id,
    get_trip_by_id,
    update_trip,
)
from models.location_model import (
    get_all_locations,
    add_new_location,
    get_location_by_id,
    update_location,
    delete_location_by_id,
)

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


@admin_bp.route("/routes", methods=["GET"], endpoint="manage_routes")
def manage_routes():
    routes = get_all_routes()
    locations = get_all_locations()
    return render_template("admin/routes.html", routes=routes, locations=locations)


@admin_bp.route("/routes/add", methods=["POST"], endpoint="add_route")
def add_route():
    data = request.form
    try:
        add_new_route(
            data["source_id"],
            data["destination_id"],
            data["distance"],
            data["estimated_time"] + " hours",
        )
        flash("Route added successfully.", "success")
    except Exception as e:
        flash(f"Error adding route: {e}", "danger")
    return redirect(url_for("admin.manage_routes"))


@admin_bp.route(
    "/routes/edit/<int:route_id>", methods=["GET", "POST"], endpoint="edit_route"
)
def edit_route(route_id):
    if request.method == "POST":
        data = request.form
        try:
            update_route(
                route_id,
                data["source_id"],
                data["destination_id"],
                data["distance"],
                data["estimated_time"],
            )
            flash("Route updated successfully.", "success")
            return redirect(url_for("admin.manage_routes"))
        except Exception as e:
            flash(f"Error updating route: {e}", "danger")

    route = get_route_by_id(route_id)
    locations = get_all_locations()  # Already defined earlier
    return render_template("admin/edit_route.html", route=route, locations=locations)


@admin_bp.route(
    "/routes/delete/<int:route_id>", methods=["POST"], endpoint="delete_route"
)
def delete_route(route_id):
    try:
        delete_route_by_id(route_id)
        flash("Route deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting route: {e}", "danger")
    return redirect(url_for("admin.manage_routes"))


# -------------------------
# buses management
# -------------------------
@admin_bp.route("/buses", methods=["GET"], endpoint="manage_buses")
def manage_buses():
    buses = get_all_buses()
    routes = get_all_routes()
    return render_template("admin/buses.html", buses=buses, routes=routes)


@admin_bp.route("/buses/add", methods=["POST"], endpoint="add_bus")
def add_bus():
    data = request.form
    try:
        add_new_bus(
            data["bus_number"], data["capacity"], data["bus_type"], data["route_id"]
        )
        flash("Bus added successfully.", "success")
    except Exception as e:
        flash(f"Error adding bus: {e}", "danger")
    return redirect(url_for("admin.manage_buses"))


@admin_bp.route(
    "/buses/edit/<int:bus_id>", methods=["GET", "POST"], endpoint="edit_bus"
)
def edit_bus(bus_id):
    if request.method == "POST":
        data = request.form
        try:
            update_bus(
                bus_id,
                data["bus_number"],
                data["capacity"],
                data["bus_type"],
                data["route_id"],
            )
            flash("Bus updated successfully.", "success")
            return redirect(url_for("admin.manage_buses"))
        except Exception as e:
            flash(f"Error updating bus: {e}", "danger")

    bus = get_bus_by_id(bus_id)
    routes = get_all_routes()
    return render_template("admin/edit_bus.html", bus=bus, routes=routes)


@admin_bp.route("/buses/delete/<int:bus_id>", methods=["POST"], endpoint="delete_bus")
def delete_bus(bus_id):
    try:
        delete_bus_by_id(bus_id)
        flash("Bus deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting bus: {e}", "danger")
    return redirect(url_for("admin.manage_buses"))


# -------------------------
# locations management
# -------------------------
@admin_bp.route("/locations", methods=["GET"], endpoint="manage_locations")
def manage_locations():
    locations = get_all_locations()
    return render_template("admin/locations.html", locations=locations)


@admin_bp.route("/locations/add", methods=["POST"], endpoint="add_location")
def add_location():
    data = request.form
    try:
        add_new_location(data["city"], data["state"], data["pincode"])
        flash("Location added successfully.", "success")
    except Exception as e:
        flash(f"Error adding location: {e}", "danger")
    return redirect(url_for("admin.manage_locations"))


@admin_bp.route(
    "/locations/edit/<int:location_id>",
    methods=["GET", "POST"],
    endpoint="edit_location",
)
def edit_location(location_id):
    if request.method == "POST":
        data = request.form
        try:
            update_location(location_id, data["city"], data["state"], data["pincode"])
            flash("Location updated successfully.", "success")
            return redirect(url_for("admin.manage_locations"))
        except Exception as e:
            flash(f"Error updating location: {e}", "danger")

    location = get_location_by_id(location_id)
    return render_template("admin/edit_location.html", location=location)


@admin_bp.route(
    "/locations/delete/<int:location_id>", methods=["POST"], endpoint="delete_location"
)
def delete_location(location_id):
    try:
        delete_location_by_id(location_id)
        flash("Location deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting location: {e}", "danger")
    return redirect(url_for("admin.manage_locations"))


# -------------------------
# booking reports
# -------------------------
@admin_bp.route("/reports/bookings", methods=["GET"], endpoint="booking_reports")
def booking_reports():
    reports = get_daily_booking_revenue()
    return render_template("admin/booking_reports.html", reports=reports)

