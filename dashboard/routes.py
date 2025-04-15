from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.trip_model import search_trips
from models.review_model import upsert_review
from models.booking_model import (
    get_customer_bookings,
    get_available_seats,
    create_booking_and_payment,
    get_booking_with_seats_and_review,
)


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
def dashboard():
    if "id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")


@dashboard_bp.route("/mybookings")
def my_bookings():
    #customer_id = session["id"]

    #if not customer_id:
    #    return redirect(url_for("auth.login"))

    bookings = get_customer_bookings(customer_id)
    return render_template("my_bookings.html", bookings=bookings)


@dashboard_bp.route("/mybookings/<int:booking_id>", methods=["GET", "POST"])
def booking_details(booking_id):
    customer_id = session.get("user_id")

    if request.method == "POST":
        rating = request.form["rating"]
        comment = request.form["comment"]
        if not rating:
            flash("Rating is required.", "warning")
        else:
            upsert_review(customer_id, booking_id, rating, comment)
            flash("Review submitted successfully.", "success")
        return redirect(url_for("dashboard.my_bookings"))

    # For GET request
    booking, seats, review = get_booking_with_seats_and_review(customer_id, booking_id)
    if not booking:
        flash("Booking not found or access denied.", "danger")
        return redirect(url_for("dashboard.my_bookings"))

    return render_template(
        "booking_details.html", booking=booking, seats=seats, review=review
    )


@dashboard_bp.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        source = request.form["source"]
        destination = request.form["destination"]
        date = request.form["date"]

        trips = search_trips(source, destination, date)
        return render_template("trip_results.html", trips=trips)

    return render_template("trip_search.html")


@dashboard_bp.route("/book/<int:trip_id>/")
def seat_selection(trip_id):
    #customer_id = session["id"]

    #if not customer_id:
    #    return redirect(url_for("auth.login"))

    seats = get_available_seats(trip_id)
    return render_template("seat_selection.html", trip_id=trip_id, seats=seats)

@dashboard_bp.route("/book/<int:trip_id>/pay/init", methods=["POST"])
def show_payment_page(trip_id):
    # Get selected seats from POST
    seat_numbers = request.form.getlist("seats")
    
    if not seat_numbers:
        flash("Please select at least one seat.", "warning")
        return redirect(url_for("dashboard.seat_selection", trip_id=trip_id))
    
    return render_template("payment.html", trip_id=trip_id, seat_numbers=seat_numbers)

@dashboard_bp.route("/book/<int:trip_id>/pay", methods=["GET", "POST"])
def payment(trip_id):
    if request.method == "POST":
        customer_id = 1
        payment_method = request.form.get("payment_method")  # UPI, Card, etc.
        seat_numbers = request.form.getlist("seats")  # Passed from hidden inputs

        print("Seats received:", seat_numbers)
        print("Payment method:", payment_method)


        if not all([customer_id, payment_method, seat_numbers]):
            flash("Missing payment or seat data.", "danger")
            return redirect(url_for("dashboard.seat_selection", trip_id=trip_id))

        success = create_booking_and_payment(
            customer_id, trip_id, seat_numbers, payment_method
        )
        if not success:
            flash("Payment failed or seat conflict. Please try again.", "danger")
            return redirect(url_for("dashboard.seat_selection", trip_id=trip_id))

        flash("Payment successful. Booking confirmed!", "success")
        return redirect(url_for("dashboard.my_bookings"))

    return render_template("payment.html", trip_id=trip_id)
