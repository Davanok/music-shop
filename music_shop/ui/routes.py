from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import (
    DEFAULT_IMAGE,
    add_to_cart,
    cart_items,
    cart_totals,
    place_order,
    product_gallery,
    product_payload_from_form,
    slugify,
    update_cart,
)

ui = Blueprint("ui", __name__)


@ui.route("/")
def home():
    filters = {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "all"),
        "stock": request.args.get("stock", "all"),
    }
    return render_template(
        "home.html",
        categories=repo.list_categories(),
        featured=repo.list_products(featured_only=True, limit=3),
        products=repo.list_products(search=filters["q"], category_slug=filters["category"], stock=filters["stock"]),
        filters=filters,
    )


@ui.route("/products/<slug>")
def product_detail(slug):
    product = repo.get_product_by_slug(slug)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("ui.home"))
    return render_template("product_detail.html", product=product, gallery=product_gallery(product))


@ui.post("/cart/add/<int:product_id>")
def add_cart_item(product_id):
    if add_to_cart(product_id, request.form.get("quantity", 1)):
        flash("Added item to cart.", "success")
    else:
        flash("That product is currently out of stock.", "error")
    return redirect(request.referrer or url_for("ui.cart"))


@ui.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        quantities = {
            key.replace("quantity_", ""): int(value or 0)
            for key, value in request.form.items()
            if key.startswith("quantity_")
        }
        update_cart(quantities)
        flash("Cart updated.", "success")
        return redirect(url_for("ui.cart"))
    items = cart_items()
    return render_template("cart.html", items=items, totals=cart_totals(items))


@ui.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("ui.cart"))
    totals = cart_totals(items)
    if request.method == "POST":
        try:
            order = place_order(
                request.form["name"].strip(),
                request.form["email"].strip().lower(),
                request.form["address"].strip(),
                items,
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("ui.cart"))
        flash("Order placed successfully.", "success")
        return redirect(url_for("ui.confirmation", order_number=order.order_number))
    return render_template("checkout.html", items=items, totals=totals)


@ui.route("/confirmation/<order_number>")
def confirmation(order_number):
    order = repo.get_order_by_number(order_number)
    if not order:
        return redirect(url_for("ui.home"))
    return render_template("confirmation.html", order=order)


@ui.route("/account")
def account():
    email = request.args.get("email", "").strip().lower()
    orders = repo.list_orders_for_email(email) if email else []
    return render_template("account.html", email=email, orders=orders)


@ui.route("/admin")
def admin_dashboard():
    categories = repo.list_categories()
    products = repo.list_products()
    orders = repo.list_orders()
    return render_template("admin/dashboard.html", categories=categories, products=products, orders=orders, revenue=repo.total_revenue())


@ui.route("/admin/products/new", methods=["GET", "POST"])
@ui.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
def admin_product_form(product_id=None):
    product = repo.get_product(product_id) if product_id else None
    if request.method == "POST":
        try:
            repo.save_product(product, **product_payload_from_form(request.form, request.files, product))
            flash("Product updated." if product else "Product created.", "success")
            return redirect(url_for("ui.admin_dashboard"))
        except IntegrityError:
            db.session.rollback()
            flash("Product slug must be unique.", "error")
    return render_template("admin/product_form.html", product=product, categories=repo.list_categories())


@ui.post("/admin/products/<int:product_id>/delete")
def admin_delete_product(product_id):
    try:
        repo.delete_product(product_id)
        flash("Product deleted.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Product cannot be deleted because it belongs to an order.", "error")
    return redirect(url_for("ui.admin_dashboard"))


@ui.post("/admin/categories")
def admin_add_category():
    try:
        name = request.form["name"].strip()
        repo.create_category(
            slug=slugify(name),
            name=name,
            description=request.form.get("description") or "Custom admin-created category.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Category added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Category slug must be unique.", "error")
    return redirect(url_for("ui.admin_dashboard"))


@ui.post("/admin/categories/<int:category_id>/delete")
def admin_delete_category(category_id):
    try:
        repo.delete_category(category_id)
        flash("Category deleted.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Category cannot be deleted while products use it.", "error")
    return redirect(url_for("ui.admin_dashboard"))
