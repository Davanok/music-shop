from flask import Blueprint, flash, redirect, render_template, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash

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
    return render_template(
        "account.html",
        orders=orders,
        user=user,
        errors={}
    )


@bp.route("/account/profile", methods=["GET", "POST"])
def profile():
    user = current_user()
    if not user:
        flash("Войдите, чтобы редактировать профиль.", "error")
        return redirect(url_for("auth.login"))

    errors = {}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate name
        if not name:
            errors["name"] = "Имя не может быть пустым."

        # Validate email
        if not email or "@" not in email:
            errors["email"] = "Введите корректный email."
        elif email != user.email:
            existing = repo.get_user_by_email(email)
            if existing and existing.id != user.id:
                errors["email"] = "Этот email уже используется."

        # Password change is optional — only validate if any field filled
        new_password_hash = None
        if current_password or new_password or confirm_password:
            if not check_password_hash(user.password_hash, current_password):
                errors["current_password"] = "Неверный текущий пароль."
            elif len(new_password) < 8:
                errors["new_password"] = "Новый пароль должен содержать не менее 8 символов."
            elif new_password != confirm_password:
                errors["confirm_password"] = "Пароли не совпадают."
            else:
                new_password_hash = generate_password_hash(new_password)

        if not errors:
            repo.update_user(
                user_id=user.id,
                email=email,
                name=name,
                role=user.role,
                password_hash=new_password_hash,
            )
            flash("Данные успешно сохранены.", "success")
            return redirect(url_for("account.profile"))

    orders = repo.list_orders_for_email(user.email)
    return render_template(
        "account_profile.html",
        orders=orders,
        user=user,
        errors=errors
    )
