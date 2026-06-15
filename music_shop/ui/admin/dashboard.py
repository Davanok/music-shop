from flask import render_template, request, Blueprint, flash, redirect, url_for
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

    # Получаем все необходимые данные
    categories = repo.list_categories()
    products = repo.list_products()
    orders = repo.list_orders()
    users = repo.list_users()
    reviews = repo.list_reviews()
    revenue = repo.total_revenue()

    # Получаем выбранные записи
    selected_product = None
    selected_category = None
    selected_user = None
    selected_order = None
    selected_review = None

    if entry_id:
        if active_section == "products":
            selected_product = repo.get_product(entry_id)
        elif active_section == "categories":
            selected_category = repo.get_category(entry_id)
        elif active_section == "users":
            selected_user = repo.get_user(entry_id)
        elif active_section == "orders":
            selected_order = repo.get_order(entry_id)
        elif active_section == "reviews":
            selected_review = repo.get_review(entry_id)

    # Определяем, какой шаблон рендерить
    is_spa = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    spa_request_type = request.headers.get("X-SPA-Request")

    if is_spa:
        if spa_request_type == "section":
            # Возвращаем только основную панель (таблицу)
            return render_template(
                "admin/partials/section_content.html",
                active_section=active_section,
                categories=categories,
                products=products,
                orders=orders,
                users=users,
                reviews=reviews,
                role_labels=ROLE_LABELS,
                selected_product=selected_product,
                selected_category=selected_category,
                selected_user=selected_user,
                selected_order=selected_order,
                selected_review=selected_review,
            )
        elif spa_request_type == "entry":
            # Возвращаем обе панели (таблицу и форму)
            return render_template(
                "admin/partials/entry_response.html",
                active_section=active_section,
                categories=categories,
                products=products,
                orders=orders,
                users=users,
                reviews=reviews,
                role_labels=ROLE_LABELS,
                selected_product=selected_product,
                selected_category=selected_category,
                selected_user=selected_user,
                selected_order=selected_order,
                selected_review=selected_review,
                is_adding=is_adding,
            )
        else:
            # Возвращаем только форму (для AJAX POST запросов)
            return render_template(
                "admin/partials/form_only.html",
                active_section=active_section,
                categories=categories,
                products=products,
                selected_product=selected_product,
                selected_category=selected_category,
                selected_user=selected_user,
                selected_order=selected_order,
                selected_review=selected_review,
                is_adding=is_adding,
                role_labels=ROLE_LABELS,
                order_statuses=list(OrderStatus),
            )

    # Полный рендер страницы
    return render_template(
        "admin/dashboard.html",
        active_section=active_section,
        categories=categories,
        products=products,
        orders=orders,
        revenue=revenue,
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
