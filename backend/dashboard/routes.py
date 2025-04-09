from flask import Blueprint, render_template, request, redirect, url_for, session, flash

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
def dashboard():
    if "id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")
