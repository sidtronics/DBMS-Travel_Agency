from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def admin():
    if "id" not in session or session["admin"] != "yes":
        return redirect(url_for("auth.login"))

    return render_template("admin.html")
