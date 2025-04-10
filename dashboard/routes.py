from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.booking_model import (
    get_customer_bookings,
    search_trips,
    get_available_seats,
    book_selected_seats,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
def dashboard():
    if "id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")


@dashboard_bp.route("/mybookings")
def my_bookings():
    customer_id = session["id"]

    if not customer_id:
        return redirect(url_for("auth.login"))

    bookings = get_customer_bookings(customer_id)
    return render_template("my_bookings.html", bookings=bookings)


@dashboard_bp.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        source = request.form["source"]
        destination = request.form["destination"]
        date = request.form["date"]

        trips = search_trips(source, destination, date)
        return render_template("trip_results.html", trips=trips)

    return render_template("trip_search.html")


@dashboard_bp.route("/book/<int:trip_id>/", methods=["GET", "POST"])
def seat_selection(trip_id):
    if request.method == "POST":
        selected_seats = request.form.getlist(
            "seats"
        )  # comes from form input checkboxes
        if not selected_seats:
            flash("No seats selected!", "warning")
            return redirect(url_for("dashboard.seat_selection", trip_id=trip_id))

        success = book_selected_seats(trip_id, selected_seats)
        if not success:
            flash("One or more seats are already booked. Please try again.", "danger")
            return redirect(url_for("dashboard.seat_selection", trip_id=trip_id))

        flash(f'Successfully booked seats: {", ".join(selected_seats)}', "success")
        return redirect(url_for("dashboard.my_bookings"))  # or payment page

    # GET method: show available seats
    seats = get_available_seats(trip_id)
    return render_template("seat_selection.html", trip_id=trip_id, seats=seats)
