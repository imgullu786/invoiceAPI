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


# ------------- INVOICES -------------

@api_bp.route("/invoices", methods=["GET"])
@login_required
def list_invoices():
    invoices = [
        invoice_to_dict(inv)
        for inv in Invoice.select().where(Invoice.user == current_user)
    ]
    return jsonify(invoices)


@api_bp.route("/invoices", methods=["POST"])
@login_required
def create_invoice():
    """
    JSON example:
    {
      "customer_id": 1,
      "issue_date": "2025-11-23",
      "due_date": "2025-12-01",
      "status": "draft",
      "items": [
        { "item_id": 1, "quantity": 2 },
        { "item_id": 2, "quantity": 1, "unit_price": 150.0 }
      ]
    }
    """
    data = request.get_json() or {}
    customer_id = data.get("customer_id")

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    customer = get_customer_for_user(customer_id)
    if not customer:
        return jsonify({"error": "customer not found"}), 400

    inv = Invoice.create(
        user=current_user,
        customer=customer,
        issue_date=parse_date(data.get("issue_date")) or date.today(),
        due_date=parse_date(data.get("due_date")),
        status=data.get("status") or "draft",
    )

    items_data = data.get("items") or []
    for row in items_data:
        item_id = row.get("item_id")
        quantity = row.get("quantity", 1)

        if not item_id:
            continue

        catalog_item = get_item_for_user(item_id)
        if not catalog_item:
            return jsonify({"error": f"item {item_id} not found"}), 400

        unit_price = row.get("unit_price", catalog_item.unit_price)

        InvoiceItem.create(
            invoice=inv,
            item=catalog_item,
            quantity=quantity,
            unit_price=unit_price,
        )

    # 👇 recalc stored total after creating all items
    recalc_invoice_total(inv)

    inv = get_invoice_for_user(inv.id)
    return jsonify(invoice_to_dict(inv, include_items=True)), 201


@api_bp.route("/invoices/<int:invoice_id>", methods=["GET"])
@login_required
def get_invoice(invoice_id):
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "not found"}), 404
    return jsonify(invoice_to_dict(inv, include_items=True))


@api_bp.route("/invoices/<int:invoice_id>", methods=["PUT", "PATCH"])
@login_required
def update_invoice(invoice_id):
    """
    Update invoice fields, and optionally replace its items:

    {
      "status": "paid",
      "items": [
        { "item_id": 1, "quantity": 3 },
        { "item_id": 2, "quantity": 1, "unit_price": 200.0 }
      ]
    }
    """
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}

    if "customer_id" in data:
        customer = get_customer_for_user(data["customer_id"])
        if not customer:
            return jsonify({"error": "customer not found"}), 400
        inv.customer = customer

    if "issue_date" in data:
        inv.issue_date = parse_date(data["issue_date"])
    if "due_date" in data:
        inv.due_date = parse_date(data["due_date"])
    if "status" in data:
        inv.status = data["status"]

    inv.save()

    # If items provided, replace all invoice line items
    if "items" in data:
        InvoiceItem.delete().where(InvoiceItem.invoice == inv).execute()
        for row in data["items"] or []:
            item_id = row.get("item_id")
            quantity = row.get("quantity", 1)

            if not item_id:
                continue

            catalog_item = get_item_for_user(item_id)
            if not catalog_item:
                return jsonify({"error": f"item {item_id} not found"}), 400

            unit_price = row.get("unit_price", catalog_item.unit_price)

            InvoiceItem.create(
                invoice=inv,
                item=catalog_item,
                quantity=quantity,
                unit_price=unit_price,
            )

        # recalc total after changing items
        recalc_invoice_total(inv)

    inv = get_invoice_for_user(invoice_id)
    return jsonify(invoice_to_dict(inv, include_items=True))


@api_bp.route("/invoices/<int:invoice_id>", methods=["DELETE"])
@login_required
def delete_invoice(invoice_id):
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "not found"}), 404

    inv.delete_instance(recursive=True)
    return jsonify({"message": "deleted"}), 200


# ---------- INVOICE LINE ITEMS -------------

@api_bp.route("/invoices/<int:invoice_id>/items", methods=["GET"])
@login_required
def list_invoice_items(invoice_id):
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "invoice not found"}), 404

    items = [invoice_item_to_dict(li) for li in inv.invoice_items]
    return jsonify(items)


@api_bp.route("/invoices/<int:invoice_id>/items", methods=["POST"])
@login_required
def add_invoice_item(invoice_id):
    """
    JSON:
    {
      "item_id": 1,
      "quantity": 2,
      "unit_price": 120.0   # optional, default = catalog price
    }
    """
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "invoice not found"}), 404

    data = request.get_json() or {}
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"error": "item_id is required"}), 400

    catalog_item = get_item_for_user(item_id)
    if not catalog_item:
        return jsonify({"error": "item not found"}), 400

    quantity = data.get("quantity", 1)
    unit_price = data.get("unit_price", catalog_item.unit_price)

    li = InvoiceItem.create(
        invoice=inv,
        item=catalog_item,
        quantity=quantity,
        unit_price=unit_price,
    )

    # 👇 recalc total after adding a line
    recalc_invoice_total(inv)

    return jsonify(invoice_item_to_dict(li)), 201


@api_bp.route("/invoice-items/<int:line_id>", methods=["GET"])
@login_required
def get_invoice_item(line_id):
    try:
        li = InvoiceItem.get_by_id(line_id)
    except InvoiceItem.DoesNotExist:
        return jsonify({"error": "not found"}), 404

    # enforce ownership via invoice -> user
    if li.invoice.user != current_user:
        return jsonify({"error": "not found"}), 404

    return jsonify(invoice_item_to_dict(li))


@api_bp.route("/invoice-items/<int:line_id>", methods=["PUT", "PATCH"])
@login_required
def update_invoice_item(line_id):
    try:
        li = InvoiceItem.get_by_id(line_id)
    except InvoiceItem.DoesNotExist:
        return jsonify({"error": "not found"}), 404

    if li.invoice.user != current_user:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}
    if "quantity" in data:
        li.quantity = data["quantity"]
    if "unit_price" in data:
        li.unit_price = data["unit_price"]
    li.save()

    # 👇 recalc total after updating a line
    recalc_invoice_total(li.invoice)

    return jsonify(invoice_item_to_dict(li))


@api_bp.route("/invoice-items/<int:line_id>", methods=["DELETE"])
@login_required
def delete_invoice_item(line_id):
    try:
        li = InvoiceItem.get_by_id(line_id)
    except InvoiceItem.DoesNotExist:
        return jsonify({"error": "not found"}), 404

    if li.invoice.user != current_user:
        return jsonify({"error": "not found"}), 404

    inv = li.invoice
    li.delete_instance()

    # 👇 recalc total after deleting a line
    recalc_invoice_total(inv)

    return "", 204



# ---------  INVOICE PDF (WeasyPrint) -----

@api_bp.route("/invoices/<int:invoice_id>/pdf", methods=["GET"])
@login_required
def invoice_pdf(invoice_id):
    inv = get_invoice_for_user(invoice_id)
    if not inv:
        return jsonify({"error": "not found"}), 404

    customer = inv.customer
    items = list(inv.invoice_items)

    html = render_template(
        "invoice.html",
        invoice=inv,
        customer=customer,
        items=items,
    )

    pdf_bytes = HTML(string=html).write_pdf()

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'inline; filename="invoice-{inv.id}.pdf"'
    )
    return response
