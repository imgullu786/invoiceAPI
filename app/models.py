from datetime import date
import os

from peewee import (
    Model, SqliteDatabase, CharField, TextField,
    DateField, ForeignKeyField, IntegerField, DecimalField
)
from flask_login import UserMixin
DATABASE_PATH = os.getenv("DATABASE_PATH", "invoicing.db")

db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()


class Customer(BaseModel):
    # owner
    user = ForeignKeyField(User, backref="customers", on_delete="CASCADE")

    name = CharField()
    email = CharField(null=True)
    address = TextField(null=True)
    phone = CharField(null=True)


class Invoice(BaseModel):
    # owner
    user = ForeignKeyField(User, backref="invoices", on_delete="CASCADE")

    customer = ForeignKeyField(Customer, backref="invoices", on_delete="CASCADE")
    issue_date = DateField(default=date.today)
    due_date = DateField(null=True)
    status = CharField(default="sent")  # sent, paid, etc.
    total = DecimalField(max_digits=10, decimal_places=2, default=0)


# CATALOG ITEM (maintained by user)
class Item(BaseModel):
    # owner
    user = ForeignKeyField(User, backref="items", on_delete="CASCADE")

    name = CharField()
    description = TextField(null=True)
    unit_price = DecimalField(max_digits=10, decimal_places=2)


# LINE ITEM ON INVOICE (joins Invoice + Item)
class InvoiceItem(BaseModel):
    invoice = ForeignKeyField(Invoice, backref="invoice_items", on_delete="CASCADE")
    item = ForeignKeyField(Item, backref="invoice_items", on_delete="CASCADE")
    quantity = IntegerField(default=1)
    # snapshot price at time of invoice (can override catalog price)
    unit_price = DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price


def create_tables():
    with db:
        db.create_tables([User, Customer, Invoice, Item, InvoiceItem])
