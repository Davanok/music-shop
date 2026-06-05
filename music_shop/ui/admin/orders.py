from flask import flash, redirect, request, url_for, Blueprint

from music_shop.data import repositories as repo
from music_shop.data.enums import OrderStatus
from music_shop.data.services import admin_required

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.post("/<int:order_id>/status")
@admin_required
def update_status(order_id):
    status_value = request.form.get("status")
    try:
        status = OrderStatus(status_value)
    except ValueError:
        flash("Некорректный статус заказа.", "error")
        return redirect(url_for("admin.dashboard.index", section="orders", entry_id=order_id))

    repo.update_order_status(order_id, status)
    flash("Статус заказа обновлен.", "success")
    return redirect(url_for("admin.dashboard.index", section="orders", entry_id=order_id))