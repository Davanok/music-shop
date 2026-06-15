from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import manager_required, product_payload_from_form

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/new", methods=["GET", "POST"])
@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@manager_required
def form(product_id=None):
    product = repo.get_product(product_id) if product_id else None

    if request.method == "POST":
        try:
            saved_product = repo.save_product(
                product,
                **product_payload_from_form(
                    request.form,
                    request.files,
                    product
                )
            )
            flash("Товар обновлен." if product else "Товар создан.", "success")

            # Для AJAX запросов
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # Возвращаем обновленную форму и таблицу
                return _get_spa_response(
                    section="products",
                    entry_id=saved_product.id,
                    success=True,
                    message="Товар сохранен"
                )

            return redirect(url_for("admin.dashboard.index", section="products", entry_id=saved_product.id))
        except IntegrityError:
            db.session.rollback()
            flash("Адрес товара должен быть уникальным.", "error")

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return _get_spa_response(
                    section="products",
                    entry_id=product_id,
                    success=False,
                    message="Адрес товара должен быть уникальным"
                )

    # GET запрос - показываем форму
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template(
            "admin/partials/form_only.html",
            active_section="products",
            categories=repo.list_categories(),
            selected_product=product,
            is_adding=product is None,
            role_labels={},
            order_statuses=[]
        )

    return render_template(
        "admin/product_form.html",
        product=product,
        categories=repo.list_categories()
    )


@bp.post("/<int:product_id>/delete")
@manager_required
def delete(product_id):
    try:
        repo.delete_product(product_id)
        flash("Товар удален.", "success")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="products",
                entry_id=None,
                success=True,
                message="Товар удален"
            )
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить товар, который есть в заказе.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="products",
                entry_id=product_id,
                success=False,
                message="Нельзя удалить товар, который есть в заказе"
            )

    return redirect(url_for("admin.dashboard.index", section="products"))


def _get_spa_response(section, entry_id, success, message):
    """Вспомогательная функция для формирования SPA ответов"""
    from flask import jsonify

    # Получаем обновленные данные
    categories = repo.list_categories()
    products = repo.list_products()

    selected_product = repo.get_product(entry_id) if entry_id else None

    # Рендерим обновленные панели
    list_panel = render_template(
        "admin/partials/section_content.html",
        active_section=section,
        categories=categories,
        products=products,
        orders=repo.list_orders(),
        users=repo.list_users(),
        reviews=repo.list_reviews(),
        role_labels={},
        selected_product=selected_product,
        selected_category=None,
        selected_user=None,
        selected_order=None,
        selected_review=None,
    )

    form_panel = render_template(
        "admin/partials/form_only.html",
        active_section=section,
        categories=categories,
        products=products,
        selected_product=selected_product,
        selected_category=None,
        selected_user=None,
        selected_order=None,
        selected_review=None,
        is_adding=entry_id is None,
        role_labels={},
        order_statuses=[]
    )

    return jsonify({
        "success": success,
        "message": message,
        "listPanel": list_panel,
        "formPanel": form_panel
    })