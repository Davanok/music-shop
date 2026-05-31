import json
import re
import uuid
from decimal import Decimal
from functools import wraps
from pathlib import Path

from flask import current_app, flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .database import db
from .models import Order, OrderItem, Product
from .repositories import get_or_create_customer, get_product, get_user, get_user_by_email, list_products_by_ids

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80"
SHIPPING_RATE = Decimal("24.00")
ROLE_LABELS = {"admin": "Администратор", "manager": "Менеджер", "viewer": "Наблюдатель"}


def slugify(value):
    slug = re.sub(r"[^a-z0-9а-яё]+", "-", value.lower()).strip("-")
    return slug or uuid.uuid4().hex[:10]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename or not allowed_file(file_storage.filename):
        return None
    filename = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_dir / filename)
    return url_for("static", filename=f"uploads/{filename}")


def product_gallery(product):
    try:
        gallery = json.loads(product.gallery_json or "[]")
    except (TypeError, json.JSONDecodeError):
        gallery = []
    return gallery or [product.image_url]


def get_cart():
    return session.setdefault("cart", {})


def cart_count():
    return sum(int(quantity) for quantity in session.get("cart", {}).values())


def add_to_cart(product_id, quantity=1):
    product = get_product(product_id)
    if not product or product.stock < 1:
        return False
    cart = get_cart()
    current = int(cart.get(str(product_id), 0))
    cart[str(product_id)] = min(current + max(int(quantity), 1), product.stock)
    session.modified = True
    return True


def update_cart(quantities):
    cart = {}
    for product_id, quantity in quantities.items():
        product = get_product(int(product_id))
        safe_quantity = max(int(quantity), 0)
        if product and safe_quantity > 0:
            cart[str(product_id)] = min(safe_quantity, product.stock)
    session["cart"] = cart


def clear_cart():
    session["cart"] = {}


def cart_items():
    cart = session.get("cart", {})
    product_ids = [int(product_id) for product_id in cart.keys()]
    products = list_products_by_ids(product_ids)
    items = []
    for product in products:
        quantity = int(cart.get(str(product.id), 0))
        if quantity > 0:
            items.append({"product": product, "quantity": quantity, "line_total": product.price * quantity})
    return items


def cart_totals(items=None):
    items = cart_items() if items is None else items
    subtotal = sum((item["line_total"] for item in items), Decimal("0.00"))
    shipping = SHIPPING_RATE if subtotal > 0 else Decimal("0.00")
    return {"subtotal": subtotal, "shipping": shipping, "total": subtotal + shipping}


def place_order(name, email, address, items=None):
    items = cart_items() if items is None else items
    if not items:
        raise ValueError("Корзина пуста")
    totals = cart_totals(items)
    try:
        customer = get_or_create_customer(name=name, email=email, address=address)
        order = Order(order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}", customer=customer, **totals)
        db.session.add(order)
        db.session.flush()
        for item in items:
            product = db.session.get(Product, item["product"].id, with_for_update=True)
            if product.stock < item["quantity"]:
                raise ValueError(f"Недостаточно товара на складе: {product.name}.")
            product.stock -= item["quantity"]
            order.items.append(
                OrderItem(
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=item["quantity"],
                    line_total=item["line_total"],
                )
            )
        db.session.commit()
        clear_cart()
        return order
    except Exception:
        db.session.rollback()
        raise


def product_payload_from_form(form, files, product=None):
    image_url = save_uploaded_image(files.get("image_file")) or form.get("image_url") or (product.image_url if product else None) or DEFAULT_IMAGE
    return {
        "slug": slugify(form.get("slug") or form["name"]),
        "name": form["name"].strip(),
        "category_id": int(form["category_id"]),
        "description": form["description"].strip(),
        "price": Decimal(form["price"]),
        "stock": int(form["stock"]),
        "featured": bool(form.get("featured")),
        "image_url": image_url,
        "gallery_json": json.dumps([image_url]),
    }


def to_product_dict(product):
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "category": product.category.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "featured": product.featured,
        "image_url": product.image_url,
    }


def cart_payload(items=None):
    items = cart_items() if items is None else items
    totals = cart_totals(items)
    return {
        "count": cart_count(),
        "items": [
            {
                "product": to_product_dict(item["product"]),
                "quantity": item["quantity"],
                "line_total": str(item["line_total"]),
            }
            for item in items
        ],
        "totals": {key: str(value) for key, value in totals.items()},
    }


def hash_password(password):
    return generate_password_hash(password)


def authenticate_user(email, password):
    user = get_user_by_email(email.strip().lower())
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def login_user(user):
    session["user_id"] = user.id


def logout_user():
    session.pop("user_id", None)


def current_user():
    user_id = session.get("user_id")
    return get_user(user_id) if user_id else None


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Войдите как администратор, чтобы открыть панель управления.", "error")
            return redirect(url_for("ui.login"))
        if not user.is_admin:
            flash("У вас нет прав администратора для управления товарами и ролями.", "error")
            return redirect(url_for("ui.home"))
        return view(*args, **kwargs)

    return wrapped
