# 📄 Invoice API

A fully-featured **Invoice Management API** built with **Flask**, **Peewee ORM**, **WeasyPrint**, and **Flask-Login**.

Supports multi-user accounts, customer & item catalogs, invoices with line items, **PDF generation**, and complete **CRUD** operations.

---

## 🚀 Features

### 🔐 Authentication
* User registration & login (**Flask-Login**)
* Session-based authentication
* Each user sees only their own data
    * Customers
    * Items
    * Invoices
    * Invoice line items

### 👥 Customers
* **Create, list, update, delete**
* Each customer belongs to a user
* Customer details appear in PDF invoices

### 🛒 Items (Catalog)
* User-managed catalog of products/services
* **Create, list, update, delete**
* Used when building invoices

### 🧾 Invoices
* **Create** invoices for customers
* Add multiple **invoice items**
* Stored invoice total
* **Update, list, delete**
* **Generate professional PDF invoices**

### 📄 PDF Generation
* Clean invoice layout
* Includes customer, invoice details
* Items with quantity, unit price, line totals
* Built with **WeasyPrint**

---

## ⚙️ Environment Config
* `.env` for secrets + DB config
* Easy to switch environments

## 📦 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Flask |
| **ORM** | Peewee |
| **Auth** | Flask-Login |
| **PDF Engine** | WeasyPrint |
| **DB** | SQLite (configurable via `.env`) |
| **Env Loader** | python-dotenv |


## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone [https://github.com/yourusername/invoice-api.git](https://github.com/yourusername/invoice-api.git)
cd invoice-api
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
```
### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install WeasyPrint System Dependencies

**Ubuntu / Debian:**

```bash
sudo apt install -y \
    libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```
### 🔐 Configure Environment Variables

Create a **`.env`** file in the project root:

```ini
FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=invoicing.db
```
### ▶️ Run the Application

Start server:

```bash
pythin run.py
```
API URL
```bash
http://127.0.0.1:5000
```

## 🧪 Testing Using Bruno/Postman

### Register

**`POST /auth/register`**

```json
{
  "username": "admin",
  "password": "secret"
}
```

### Login

**`POST /auth/login`**

> Automatically stored cookies as Flask-login handling Auth
> All subsequent requests use the session

## 📘 API Overview

### 🔐 Authentication Routes

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| POST | `/auth/register` | Create user |
| POST | `/auth/login` | Login user |
| POST | `/auth/logout` | Logout user |

### 👥 Customers

| Method | Endpoint |
| :--- | :--- |
| GET | `/customers` |
| POST | `/customers` |
| GET | `/customers/<id>` |
| PATCH | `/customers/<id>` |
| DELETE | `/customers/<id>` |

**`Example Create Customers`**
```bash
{
  "name": "Sujal",
  "email": "sujal@gmail.com",
  "address": "Nagpur",
  "phone": "9999999999"
}
```


### 🛒 Items (Catalog)

| Method | Endpoint |
| :--- | :--- |
| GET | `/items` |
| POST | `/items` |
| GET | `/items/<id>` |
| PATCH | `/items/<id>` |
| DELETE | `/items/<id>` |

**`Example Create Items`**
```bash
{
    "name": "Deployment Service",
    "description": "Per hour deployment service rate",
    "unit_price": 200.0
}
```

### 🧾 Invoices

| Method | Endpoint |
| :--- | :--- |
| GET | `/invoices` |
| POST | `/invoices` |
| GET | `/invoices/<id>` |
| PATCH | `/invoices/<id>` |
| DELETE | `/invoices/<id>` |
| GET | `/invoices/<id>/pdf` |

**`Example Create Invoice`**
```bash
{
  "customer_id": 1,
  "status": "sent",
  "items": [
    { "item_id": 1, "quantity": 2 },
    { "item_id": 2, "quantity": 1, "unit_price": 150 }
  ]
}
```

### 📦 Invoice Items

| Method | Endpoint |
| :--- | :--- |
| GET | `/invoices/<invoice_id>/items` |
| POST | `/invoices/<invoice_id>/items` |
| GET | `/invoice-items/<line_id>` |
| PATCH | `/invoice-items/<line_id>` |
| DELETE | `/invoice-items/<line_id>` |


### Frontend Routes (Server-Rendered)

| Routes | Description |
| :--- | :--- |
| /login | Login form. |
| /register | User signup page. |
| /dashboard | Overview of counts: customers, items, invoices. |
| /customers-ui | Full customer management (list, create, edit, delete). |
| /items-ui | Catalog management for items (list, create, edit, delete). |
| /invoices-ui | Invoice management UI (create, update status, edit items, delete, PDF). |