from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import admin_required, product_payload_from_form

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/new", methods=["GET", "POST"])
@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def form(product_id=None):
    product = repo.get_product(product_id) if product_id else None
    if request.method == "POST":
        try:
            saved_product = repo.save_product(product,
                                              **product_payload_from_form(request.form, request.files, product))
            flash("Товар обновлен." if product else "Товар создан.", "success")
            return redirect(url_for("admin.dashboard.index", section="products", entry_id=saved_product.id))
        except IntegrityError:
            db.session.rollback()
            flash("Адрес товара должен быть уникальным.", "error")
    return render_template("admin/product_form.html", product=product, categories=repo.list_categories())


@bp.post("/<int:product_id>/delete")
@admin_required
def delete(product_id):
    try:
        repo.delete_product(product_id)
        flash("Товар удален.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить товар, который есть в заказе.", "error")
    return redirect(url_for("admin.dashboard.index", section="products"))
