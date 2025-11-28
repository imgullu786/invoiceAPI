from flask import Blueprint, render_template

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
