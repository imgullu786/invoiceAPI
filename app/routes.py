from datetime import date

from flask import (
    Blueprint, request, jsonify,
    render_template, make_response
)
from flask_login import login_required, current_user
from weasyprint import HTML

from .models import Customer, Invoice, Item, InvoiceItem

api_bp = Blueprint("api", __name__)


# -------- Helpers ----------------
def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    # Expecting ISO string "YYYY-MM-DD"
    return date.fromisoformat(value)


def customer_to_dict(c: Customer):
    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "address": c.address,
        "phone": c.phone,
    }


def item_to_dict(it: Item):
    return {
        "id": it.id,
        "name": it.name,
        "description": it.description,
        "unit_price": float(it.unit_price),
    }


def invoice_item_to_dict(li: InvoiceItem):
    return {
        "id": li.id,
        "invoice_id": li.invoice_id,
        "item_id": li.item_id,
        "item_name": li.item.name,
        "quantity": li.quantity,
        "unit_price": float(li.unit_price),
        "total": float(li.total),
    }


def invoice_to_dict(inv: Invoice, include_items=False):
    lines = list(inv.invoice_items)

    # Prefer stored total; fall back to calculation if None
    if inv.total is not None:
        total = inv.total
    else:
        total = sum(li.total for li in lines)

    data = {
        "id": inv.id,
        "customer_id": inv.customer_id,
        "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
        "status": inv.status,
        "total": float(total),
    }
    if include_items:
        data["items"] = [invoice_item_to_dict(li) for li in lines]
    return data


def recalc_invoice_total(inv: Invoice):
    """Recalculate and store invoice.total from its line items."""
    lines = list(inv.invoice_items)
    total = sum(li.total for li in lines)
    inv.total = total
    inv.save()


# Utility: safe "get or 404" with user ownership
def get_customer_for_user(customer_id):
    try:
        return Customer.get(
            (Customer.id == customer_id) &
            (Customer.user == current_user)
        )
    except Customer.DoesNotExist:
        return None


def get_item_for_user(item_id):
    try:
        return Item.get(
            (Item.id == item_id) &
            (Item.user == current_user)
        )
    except Item.DoesNotExist:
        return None


def get_invoice_for_user(invoice_id):
    try:
        return Invoice.get(
            (Invoice.id == invoice_id) &
            (Invoice.user == current_user)
        )
    except Invoice.DoesNotExist:
        return None


# -------CUSTOMERS -------------

@api_bp.route("/customers", methods=["GET"])
@login_required
def list_customers():
    customers = [
        customer_to_dict(c)
        for c in Customer.select().where(Customer.user == current_user)
    ]
    return jsonify(customers)


@api_bp.route("/customers", methods=["POST"])
@login_required
def create_customer():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    c = Customer.create(
        user=current_user,
        name=data["name"],
        email=data.get("email"),
        address=data.get("address"),
        phone=data.get("phone"),
    )
    return jsonify(customer_to_dict(c)), 201


@api_bp.route("/customers/<int:customer_id>", methods=["GET"])
@login_required
def get_customer(customer_id):
    c = get_customer_for_user(customer_id)
    if not c:
        return jsonify({"error": "not found"}), 404
    return jsonify(customer_to_dict(c))


@api_bp.route("/customers/<int:customer_id>", methods=["PUT", "PATCH"])
@login_required
def update_customer(customer_id):
    c = get_customer_for_user(customer_id)
    if not c:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}
    for field in ["name", "email", "address", "phone"]:
        if field in data:
            setattr(c, field, data[field])
    c.save()
    return jsonify(customer_to_dict(c))


@api_bp.route("/customers/<int:customer_id>", methods=["DELETE"])
@login_required
def delete_customer(customer_id):
    c = get_customer_for_user(customer_id)
    if not c:
        return jsonify({"error": "not found"}), 404

    c.delete_instance(recursive=True)
    return jsonify({"message": "deleted"}), 200


# ----------- CATALOG ITEMS ----------------

@api_bp.route("/items", methods=["GET"])
@login_required
def list_items():
    items = [
        item_to_dict(it)
        for it in Item.select().where(Item.user == current_user)
    ]
    return jsonify(items)


@api_bp.route("/items", methods=["POST"])
@login_required
def create_item():
    """
    JSON example:
    {
      "name": "Consulting Hour",
      "description": "Per hour consulting rate",
      "unit_price": 100.0
    }
    """
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    if "unit_price" not in data:
        return jsonify({"error": "unit_price is required"}), 400

    it = Item.create(
        user=current_user,
        name=data["name"],
        description=data.get("description"),
        unit_price=data["unit_price"],
    )
    return jsonify(item_to_dict(it)), 201


@api_bp.route("/items/<int:item_id>", methods=["GET"])
@login_required
def get_item(item_id):
    it = get_item_for_user(item_id)
    if not it:
        return jsonify({"error": "not found"}), 404
    return jsonify(item_to_dict(it))


@api_bp.route("/items/<int:item_id>", methods=["PUT", "PATCH"])
@login_required
def update_item(item_id):
    it = get_item_for_user(item_id)
    if not it:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}
    for field in ["name", "description", "unit_price"]:
        if field in data:
            setattr(it, field, data[field])
    it.save()
    return jsonify(item_to_dict(it))


@api_bp.route("/items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_item(item_id):
    it = get_item_for_user(item_id)
    if not it:
        return jsonify({"error": "not found"}), 404

    it.delete_instance(recursive=True)
    return jsonify({"message": "deleted"}), 200
