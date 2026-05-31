import json
import os
import re
import uuid
from decimal import Decimal
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

import mysql.connector
from mysql.connector import Error as MySQLError

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80"
SHIPPING_RATE = Decimal("24.00")
TAX_RATE = Decimal("0.0825")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-music-shop-secret")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "static/uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)


def db_config(include_database=True):
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "music_shop"),
        "password": os.getenv("MYSQL_PASSWORD", "music_shop_password"),
    }
    if include_database:
        config["database"] = os.getenv("MYSQL_DATABASE", "music_shop")
    return config


def get_connection(dictionary=True):
    return mysql.connector.connect(**db_config(), dictionary=dictionary)


def query_all(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()


def query_one(sql, params=None):
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            connection.commit()
            return cursor.lastrowid


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or uuid.uuid4().hex[:10]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename or not allowed_file(file_storage.filename):
        return None
    filename = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
    destination = Path(app.config["UPLOAD_FOLDER"]) / filename
    file_storage.save(destination)
    return url_for("static", filename=f"uploads/{filename}")


def product_gallery(product):
    try:
        gallery = json.loads(product.get("gallery_json") or "[]")
    except (TypeError, json.JSONDecodeError):
        gallery = []
    return gallery or [product["image_url"]]


def cart_items():
    cart = session.get("cart", {})
    if not cart:
        return []
    ids = [int(product_id) for product_id in cart.keys()]
    placeholders = ",".join(["%s"] * len(ids))
    products = query_all(
        f"""
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON c.id = p.category_id
        WHERE p.id IN ({placeholders})
        ORDER BY p.name
        """,
        ids,
    )
    items = []
    for product in products:
        quantity = int(cart.get(str(product["id"]), 0))
        if quantity > 0:
            line_total = product["price"] * quantity
            items.append({"product": product, "quantity": quantity, "line_total": line_total})
    return items


def cart_totals(items=None):
    items = cart_items() if items is None else items
    subtotal = sum((item["line_total"] for item in items), Decimal("0.00"))
    shipping = SHIPPING_RATE if subtotal > 0 else Decimal("0.00")
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    return {"subtotal": subtotal, "shipping": shipping, "tax": tax, "total": subtotal + shipping + tax}


@app.context_processor
def inject_globals():
    cart_count = sum(int(quantity) for quantity in session.get("cart", {}).values())
    return {"cart_count": cart_count, "cart_totals": cart_totals}


@app.template_filter("currency")
def currency(value):
    return f"${Decimal(value):,.2f}"


@app.route("/")
def home():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "all")
    stock = request.args.get("stock", "all")
    categories = query_all("SELECT * FROM categories ORDER BY name")
    featured = query_all(
        """
        SELECT p.*, c.name AS category_name
        FROM products p JOIN categories c ON c.id = p.category_id
        WHERE featured = TRUE
        ORDER BY p.updated_at DESC LIMIT 3
        """
    )
    where = []
    params = []
    if search:
        where.append("(p.name LIKE %s OR p.description LIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if category != "all":
        where.append("c.slug = %s")
        params.append(category)
    if stock == "in-stock":
        where.append("p.stock > 0")
    elif stock == "out-of-stock":
        where.append("p.stock = 0")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    products = query_all(
        f"""
        SELECT p.*, c.name AS category_name, c.slug AS category_slug
        FROM products p JOIN categories c ON c.id = p.category_id
        {where_sql}
        ORDER BY p.featured DESC, p.name
        """,
        params,
    )
    return render_template("home.html", categories=categories, featured=featured, products=products, filters={"q": search, "category": category, "stock": stock})


@app.route("/products/<slug>")
def product_detail(slug):
    product = query_one(
        """
        SELECT p.*, c.name AS category_name
        FROM products p JOIN categories c ON c.id = p.category_id
        WHERE p.slug = %s
        """,
        (slug,),
    )
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("home"))
    return render_template("product_detail.html", product=product, gallery=product_gallery(product))


@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = query_one("SELECT id, stock FROM products WHERE id = %s", (product_id,))
    if not product or product["stock"] < 1:
        flash("That product is currently out of stock.", "error")
        return redirect(request.referrer or url_for("home"))
    quantity = max(int(request.form.get("quantity", 1)), 1)
    cart = session.setdefault("cart", {})
    current = int(cart.get(str(product_id), 0))
    cart[str(product_id)] = min(current + quantity, product["stock"])
    session.modified = True
    flash("Added item to cart.", "success")
    return redirect(request.referrer or url_for("cart"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        cart_data = {}
        for key, value in request.form.items():
            if key.startswith("quantity_"):
                product_id = key.replace("quantity_", "")
                quantity = max(int(value or 0), 0)
                if quantity:
                    cart_data[product_id] = quantity
        session["cart"] = cart_data
        flash("Cart updated.", "success")
        return redirect(url_for("cart"))
    items = cart_items()
    return render_template("cart.html", items=items, totals=cart_totals(items))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))
    totals = cart_totals(items)
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        address = request.form["address"].strip()
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM customers WHERE email = %s", (email,))
                customer = cursor.fetchone()
                if customer:
                    customer_id = customer["id"]
                    cursor.execute("UPDATE customers SET name = %s, address = %s WHERE id = %s", (name, address, customer_id))
                else:
                    cursor.execute("INSERT INTO customers (name, email, address) VALUES (%s, %s, %s)", (name, email, address))
                    customer_id = cursor.lastrowid
                order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
                cursor.execute(
                    "INSERT INTO orders (order_number, customer_id, subtotal, shipping, tax, total) VALUES (%s, %s, %s, %s, %s, %s)",
                    (order_number, customer_id, totals["subtotal"], totals["shipping"], totals["tax"], totals["total"]),
                )
                order_id = cursor.lastrowid
                for item in items:
                    product = item["product"]
                    cursor.execute("SELECT stock FROM products WHERE id = %s FOR UPDATE", (product["id"],))
                    stock_row = cursor.fetchone()
                    if stock_row["stock"] < item["quantity"]:
                        connection.rollback()
                        flash(f"Not enough stock for {product['name']}.", "error")
                        return redirect(url_for("cart"))
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, line_total) VALUES (%s, %s, %s, %s, %s, %s)",
                        (order_id, product["id"], product["name"], product["price"], item["quantity"], item["line_total"]),
                    )
                    cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item["quantity"], product["id"]))
                connection.commit()
        session["cart"] = {}
        flash("Order placed successfully.", "success")
        return redirect(url_for("confirmation", order_number=order_number))
    return render_template("checkout.html", items=items, totals=totals)


@app.route("/confirmation/<order_number>")
def confirmation(order_number):
    order = query_one(
        """
        SELECT o.*, c.name, c.email
        FROM orders o JOIN customers c ON c.id = o.customer_id
        WHERE o.order_number = %s
        """,
        (order_number,),
    )
    if not order:
        return redirect(url_for("home"))
    return render_template("confirmation.html", order=order)


@app.route("/account")
def account():
    email = request.args.get("email", "").strip().lower()
    orders = []
    if email:
        orders = query_all(
            """
            SELECT o.*, c.name, c.email
            FROM orders o JOIN customers c ON c.id = o.customer_id
            WHERE c.email = %s ORDER BY o.created_at DESC
            """,
            (email,),
        )
    return render_template("account.html", email=email, orders=orders)


@app.route("/admin")
def admin_dashboard():
    categories = query_all("SELECT * FROM categories ORDER BY name")
    products = query_all(
        """
        SELECT p.*, c.name AS category_name
        FROM products p JOIN categories c ON c.id = p.category_id
        ORDER BY p.updated_at DESC
        """
    )
    orders = query_all(
        """
        SELECT o.*, c.name AS customer_name, c.email
        FROM orders o JOIN customers c ON c.id = o.customer_id
        ORDER BY o.created_at DESC
        """
    )
    revenue_row = query_one("SELECT COALESCE(SUM(total), 0) AS revenue FROM orders")
    return render_template("admin/dashboard.html", categories=categories, products=products, orders=orders, revenue=revenue_row["revenue"])


@app.route("/admin/products/new", methods=["GET", "POST"])
@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
def admin_product_form(product_id=None):
    product = query_one("SELECT * FROM products WHERE id = %s", (product_id,)) if product_id else None
    categories = query_all("SELECT * FROM categories ORDER BY name")
    if request.method == "POST":
        image_url = save_uploaded_image(request.files.get("image_file")) or request.form.get("image_url") or (product and product["image_url"]) or DEFAULT_IMAGE
        name = request.form["name"].strip()
        slug = slugify(request.form.get("slug") or name)
        payload = (
            slug,
            name,
            int(request.form["category_id"]),
            request.form["description"].strip(),
            Decimal(request.form["price"]),
            int(request.form["stock"]),
            bool(request.form.get("featured")),
            image_url,
            json.dumps([image_url]),
        )
        if product:
            execute(
                """
                UPDATE products SET slug = %s, name = %s, category_id = %s, description = %s, price = %s, stock = %s,
                featured = %s, image_url = %s, gallery_json = %s WHERE id = %s
                """,
                (*payload, product_id),
            )
            flash("Product updated.", "success")
        else:
            execute(
                """
                INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                payload,
            )
            flash("Product created.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/product_form.html", product=product, categories=categories)


@app.post("/admin/products/<int:product_id>/delete")
def admin_delete_product(product_id):
    try:
        execute("DELETE FROM products WHERE id = %s", (product_id,))
        flash("Product deleted.", "success")
    except MySQLError:
        flash("Product cannot be deleted because it belongs to an order.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/categories", methods=["POST"])
def admin_add_category():
    name = request.form["name"].strip()
    execute(
        "INSERT INTO categories (slug, name, description, image_url) VALUES (%s, %s, %s, %s)",
        (slugify(name), name, request.form.get("description", "Custom admin-created category."), request.form.get("image_url") or DEFAULT_IMAGE),
    )
    flash("Category added.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/categories/<int:category_id>/delete", methods=["POST"])
def admin_delete_category(category_id):
    try:
        execute("DELETE FROM categories WHERE id = %s", (category_id,))
        flash("Category deleted.", "success")
    except MySQLError:
        flash("Category cannot be deleted while products use it.", "error")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
