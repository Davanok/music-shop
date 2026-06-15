from flask import flash, redirect, request, url_for, Blueprint, jsonify, render_template

from music_shop.data import repositories as repo
from music_shop.data.enums import OrderStatus
from music_shop.data.services import manager_required

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.post("/<int:order_id>/status")
@manager_required
def update_status(order_id):
    status_value = request.form.get("status")
    try:
        status = OrderStatus(status_value)
    except ValueError:
        flash("Некорректный статус заказа.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="orders",
                entry_id=order_id,
                success=False,
                message="Некорректный статус заказа"
            )

        return redirect(url_for("admin.dashboard.index", section="orders", entry_id=order_id))

    repo.update_order_status(order_id, status)
    flash("Статус заказа обновлен.", "success")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _get_spa_response(
            section="orders",
            entry_id=order_id,
            success=True,
            message="Статус заказа обновлен"
        )

    return redirect(url_for("admin.dashboard.index", section="orders", entry_id=order_id))


def _get_spa_response(section, entry_id, success, message):
    """Вспомогательная функция для формирования SPA ответов"""
    from flask import render_template

    orders = repo.list_orders()
    selected_order = repo.get_order(entry_id) if entry_id else None

    list_panel = render_template(
        "admin/partials/section_content.html",
        active_section=section,
        orders=orders,
        categories=repo.list_categories(),
        products=repo.list_products(),
        users=repo.list_users(),
        reviews=repo.list_reviews(),
        role_labels={},
        selected_order=selected_order,
        selected_product=None,
        selected_category=None,
        selected_user=None,
        selected_review=None,
    )

    form_panel = render_template(
        "admin/partials/form_only.html",
        active_section=section,
        selected_order=selected_order,
        order_statuses=list(OrderStatus),
        categories=[],
        products=[],
        role_labels={}
    )

    return jsonify({
        "success": success,
        "message": message,
        "listPanel": list_panel,
        "formPanel": form_panel
    })