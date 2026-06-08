from flask import render_template, request, Blueprint

from music_shop.data import repositories as repo
from music_shop.data.enums import OrderStatus
from music_shop.data.services import (
    ROLE_LABELS,
    admin_required,
    manager_required,
)

bp = Blueprint("dashboard", __name__)

@bp.route("")
@manager_required
def index():
    allowed_sections = {"products", "categories", "users", "orders", "reviews"}
    active_section = request.args.get("section", "products")
    if active_section not in allowed_sections:
        active_section = "products"

    entry_id = request.args.get("entry_id", type=int)
    is_adding = request.args.get("action") == "new"

    categories = repo.list_categories()
    products = repo.list_products()
    orders = repo.list_orders()
    users = repo.list_users()
    reviews = repo.list_reviews()

    selected_product = repo.get_product(entry_id) if active_section == "products" and entry_id else None
    selected_category = repo.get_category(entry_id) if active_section == "categories" and entry_id else None
    selected_user = repo.get_user(entry_id) if active_section == "users" and entry_id else None
    selected_order = repo.get_order(entry_id) if active_section == "orders" and entry_id else None
    selected_review = repo.get_review(entry_id) if active_section == "reviews" and entry_id else None

    template_name = "admin/dashboard.html"
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        template_name = f"admin/partials/{active_section}.html"

    return render_template(
        template_name,
        active_section=active_section,
        categories=categories,
        products=products,
        orders=orders,
        revenue=repo.total_revenue(),
        users=users,
        reviews=reviews,
        role_labels=ROLE_LABELS,
        order_statuses=list(OrderStatus),
        is_adding=is_adding,
        selected_product=selected_product,
        selected_category=selected_category,
        selected_user=selected_user,
        selected_order=selected_order,
        selected_review=selected_review,
    )


@bp.post("/reviews/<int:review_id>/delete")
@manager_required
def delete_review(review_id):
    repo.delete_review(review_id)
    from flask import flash, redirect, url_for
    flash("Отзыв удален.", "success")
    return redirect(url_for("admin.dashboard.index", section="reviews"))
