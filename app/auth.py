from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    JSON body:
    {
      "username": "admin",
      "password": "secret"
    }
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.select().where(User.username == username).exists():
        return jsonify({"error": "username already taken"}), 400

    user = User.create(
        username=username,
        password_hash=generate_password_hash(password),
    )

    return jsonify({"id": user.id, "username": user.username}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    JSON body:
    {
      "username": "admin",
      "password": "secret"
    }
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    try:
        user = User.get(User.username == username)
    except User.DoesNotExist:
        return jsonify({"error": "invalid credentials"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    login_user(user)
    return jsonify(
        {"message": "logged in", "user": {"id": user.id, "username": user.username}}
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logged out"})
