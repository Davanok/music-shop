from flask import Blueprint, flash, redirect, render_template, url_for

from music_shop.data import repositories as repo
from music_shop.data.services import current_user

bp = Blueprint("account", __name__)

@bp.route("/account")
def index():
    user = current_user()
    if not user:
        flash("Войдите, чтобы посмотреть историю заказов.", "error")
        return redirect(url_for("auth.login"))
    orders = repo.list_orders_for_email(user.email)
    return render_template("account.html", orders=orders)
