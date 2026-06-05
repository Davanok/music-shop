from flask import Blueprint, flash, redirect, render_template, request, url_for

from music_shop.data import repositories as repo
from music_shop.data.services import (
    add_to_cart,
    cart_items,
    cart_totals,
    current_user,
    place_order,
    update_cart,
)

bp = Blueprint("cart", __name__)


@bp.post("/cart/add/<int:product_id>")
def add_item(product_id):
    if add_to_cart(product_id, request.form.get("quantity", 1)):
        flash("Товар добавлен в корзину.", "success")
    else:
        flash("Товар сейчас недоступен.", "error")
    return redirect(request.referrer or url_for("cart.cart"))


@bp.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        quantities = {
            key.replace("quantity_", ""): int(value or 0)
            for key, value in request.form.items()
            if key.startswith("quantity_")
        }
        update_cart(quantities)
        flash("Корзина обновлена.", "success")
        return redirect(url_for("cart.cart"))
    items = cart_items()
    return render_template("cart.html", items=items, totals=cart_totals(items))


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items()
    if not items:
        flash("Ваша корзина пуста.", "error")
        return redirect(url_for("cart.cart"))
    totals = cart_totals(items)
    user = current_user()
    if not user:
        flash("Войдите, чтобы оформить заказ.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            order = place_order(
                user.name,
                user.email,
                {
                    "country": request.form.get("country", ""),
                    "city": request.form.get("city", ""),
                    "street": request.form.get("street", ""),
                    "postal_code": request.form.get("postal_code", ""),
                },
                items,
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("cart.cart"))
        flash("Заказ успешно оформлен.", "success")
        return redirect(url_for("cart.confirmation", order_number=order.order_number))
    return render_template("checkout.html", items=items, totals=totals, user=user)


@bp.route("/confirmation/<order_number>")
def confirmation(order_number):
    order = repo.get_order_by_number(order_number)
    if not order:
        return redirect(url_for("shop.home"))
    return render_template("confirmation.html", order=order)
