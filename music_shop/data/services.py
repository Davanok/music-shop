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
from .enums import OrderStatus
from .models import Address, Order, OrderItem, Product
from music_shop.data import repositories as repo

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80"
DEFAULT_DELIVERY_PRICE = Decimal("500.00")
DEFAULT_ASSEMBLY_PRICE = Decimal("1000.00")
ROLE_LABELS = {
    "admin": "Администратор",
    "manager": "Менеджер",
    "user": "Пользователь",
    "guest": "Гость"
}


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


def cart_quantities():
    quantities = {}
    for product_id, quantity in get_cart().items():
        try:
            quantities[int(product_id)] = int(quantity)
        except (TypeError, ValueError):
            continue
    return quantities


def add_to_cart(product_id, quantity=1):
    product = repo.get_product(product_id)
    if not product or product.stock < 1:
        return False

    try:
        requested_quantity = max(int(quantity), 1)
    except (TypeError, ValueError):
        requested_quantity = 1

    cart = get_cart()
    current = int(cart.get(str(product_id), 0))
    cart[str(product_id)] = min(current + requested_quantity, product.stock)
    session.modified = True
    return True


def update_cart(quantities):
    cart = {}
    for product_id, quantity in quantities.items():
        try:
            parsed_product_id = int(product_id)
            safe_quantity = max(int(quantity), 0)
        except (TypeError, ValueError):
            continue

        product = repo.get_product(parsed_product_id)
        if product and safe_quantity > 0:
            cart[str(parsed_product_id)] = min(safe_quantity, product.stock)
    session["cart"] = cart


def set_cart_quantity(product_id, quantity):
    try:
        parsed_product_id = int(product_id)
        safe_quantity = max(int(quantity), 0)
    except (TypeError, ValueError):
        return

    product = repo.get_product(parsed_product_id)
    cart = get_cart()
    if not product or safe_quantity == 0:
        cart.pop(str(parsed_product_id), None)
    else:
        cart[str(parsed_product_id)] = min(safe_quantity, product.stock)
    session.modified = True


def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True


def clear_cart():
    session["cart"] = {}


def cart_items():
    cart = session.get("cart", {})
    product_ids = []
    for product_id in cart.keys():
        try:
            product_ids.append(int(product_id))
        except (TypeError, ValueError):
            continue

    products = repo.list_products_by_ids(product_ids)
    items = []
    for product in products:
        try:
            quantity = int(cart.get(str(product.id), 0))
        except (TypeError, ValueError):
            continue
        if quantity > 0:
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "line_total": product.price * quantity,
                }
            )
    return items


def delivery_price():
    return Decimal(repo.get_setting("delivery_price", str(DEFAULT_DELIVERY_PRICE)))


def assembly_price():
    return Decimal(repo.get_setting("assembly_price", str(DEFAULT_ASSEMBLY_PRICE)))


def cart_totals(items=None, delivery_method=None, assembly_option=None):
    from .enums import DeliveryMethod, AssemblyOption
    items = cart_items() if items is None else items
    subtotal = sum((item["line_total"] for item in items), Decimal("0.00"))
    
    shipping = Decimal("0.00")
    if subtotal > 0 and (delivery_method is None or delivery_method == DeliveryMethod.DELIVERY):
        shipping = delivery_price()
        
    assembly_cost = Decimal("0.00")
    if subtotal > 0 and assembly_option == AssemblyOption.REQUIRED:
        assembly_cost = assembly_price()
        
    return {
        "subtotal": subtotal,
        "shipping": shipping,
        "assembly_cost": assembly_cost,
        "total": subtotal + shipping + assembly_cost
    }



def validate_address_data(address_data, delivery_method):
    from .enums import DeliveryMethod
    if delivery_method == DeliveryMethod.PICKUP:
        return {}
        
    required_fields = ("country", "city", "street", "postal_code")
    if not isinstance(address_data, dict):
        raise ValueError("Некорректный формат адреса")

    cleaned = {field: str(address_data.get(field, "")).strip() for field in required_fields}
    if any(not value for value in cleaned.values()):
        raise ValueError("Заполните все поля адреса доставки")
    return cleaned


def place_order(name, email, address_data, delivery_method, assembly_option, items=None):
    from .enums import DeliveryMethod, AssemblyOption
    items = cart_items() if items is None else items

    if not items:
        raise ValueError("Корзина пуста")

    user = repo.get_user_by_email(email)
    if not user:
        raise ValueError("Пользователь не найден")

    address_data = validate_address_data(address_data, delivery_method)
    totals = cart_totals(items, delivery_method, assembly_option)

    try:
        address_id = None
        if delivery_method == DeliveryMethod.DELIVERY:
            address = Address(user_id=user.id, **address_data)
            db.session.add(address)
            db.session.flush()
            address_id = address.id

        order = Order(
            order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
            user_id=user.id,
            address_id=address_id,
            status=OrderStatus.NEW,
            delivery_method=delivery_method,
            assembly_option=assembly_option,
            shipping=totals["shipping"],
            assembly_cost=totals["assembly_cost"],
        )

        db.session.add(order)
        db.session.flush()

        for item in items:
            product = db.session.get(
                Product,
                item["product"].id,
                with_for_update=True,
            )

            if not product:
                raise ValueError("Товар не найден")

            if product.stock < item["quantity"]:
                raise ValueError(
                    f"Недостаточно товара на складе: {product.name}"
                )

            product.stock -= item["quantity"]

            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    unit_price=product.price,
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
    user = repo.get_user_by_email(email.strip().lower())
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def login_user(user):
    session["user_id"] = user.id


def logout_user():
    session.pop("user_id", None)


def current_user():
    user_id = session.get("user_id")
    return repo.get_user(user_id) if user_id else None


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Пожалуйста, войдите в систему.", "error")
                return redirect(url_for("ui.login"))
            if user.role not in roles and user.role != "admin":
                flash("У вас нет прав для доступа к этой странице.", "error")
                return redirect(url_for("ui.home"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(view):
    return role_required("admin")(view)


def manager_required(view):
    return role_required("manager", "admin")(view)

