from flask import Blueprint, render_template
from flask_login import login_required, current_user

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def home():
    return render_template("login.html")


@views_bp.route("/login")
def login_page():
    return render_template("login.html")


@views_bp.route("/register")
def register_page():
    return render_template("register.html")


@views_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@views_bp.route("/customers-ui")
def customers_ui():
    return render_template("customers.html")


@views_bp.route("/items-ui")
def items_ui():
    return render_template("items.html")
