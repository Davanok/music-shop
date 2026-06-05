import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import (
    authenticate_user,
    current_user,
    hash_password,
    login_user,
    logout_user,
)

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_login_form(form):
    data = {
        "email": form.get("email", "").strip().lower(),
        "password": form.get("password", ""),
    }
    errors = {}

    if not data["email"]:
        errors["email"] = "Введите электронную почту."
    elif not EMAIL_RE.match(data["email"]):
        errors["email"] = "Введите корректный адрес электронной почты."

    if not data["password"]:
        errors["password"] = "Введите пароль."

    return data, errors


def validate_signup_form(form):
    data = {
        "name": form.get("name", "").strip(),
        "email": form.get("email", "").strip().lower(),
        "password": form.get("password", ""),
    }
    errors = {}

    if not data["name"]:
        errors["name"] = "Введите имя."
    elif len(data["name"]) < 2:
        errors["name"] = "Имя должно быть не короче 2 символов."

    if not data["email"]:
        errors["email"] = "Введите электронную почту."
    elif not EMAIL_RE.match(data["email"]):
        errors["email"] = "Введите корректный адрес электронной почты."

    if not data["password"]:
        errors["password"] = "Введите пароль."
    elif len(data["password"]) < 8:
        errors["password"] = "Пароль должен содержать минимум 8 символов."

    return data, errors


@bp.route("/login", methods=["GET", "POST"])
def login():
    user = current_user()
    if user:
        return redirect(
            url_for("admin.dashboard.index")
            if user.is_admin
            else url_for("account.index")
        )

    form = {"email": ""}
    errors = {}

    if request.method == "POST":
        form, errors = validate_login_form(request.form)

        if not errors:
            user = authenticate_user(
                form["email"],
                form["password"],
            )

            if user:
                login_user(user)

                flash("Вы вошли в систему.", "success")

                return redirect(
                    url_for("admin.dashboard.index")
                    if user.is_admin
                    else url_for("shop.home")
                )

            errors = {
                "email": "Проверьте адрес электронной почты.",
                "password": "Проверьте пароль.",
            }
            flash("Неверная электронная почта или пароль.", "error")
        else:
            flash("Исправьте ошибки в форме входа.", "error")

    return render_template("login.html", errors=errors, form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = {"name": "", "email": ""}
    errors = {}

    if request.method == "POST":
        form, errors = validate_signup_form(request.form)

        if not errors and repo.get_user_by_email(form["email"]):
            errors["email"] = "Пользователь с такой электронной почтой уже существует."

        if errors:
            flash("Исправьте ошибки в форме регистрации.", "error")
            return render_template("signup.html", errors=errors, form=form)

        try:
            user = repo.create_user(
                email=form["email"],
                name=form["name"],
                password_hash=hash_password(form["password"]),
                role="viewer",
            )

            login_user(user)

            flash(
                "Регистрация завершена. Вы вошли в систему.",
                "success",
            )

            return redirect(url_for("shop.home"))

        except IntegrityError:
            db.session.rollback()
            errors["email"] = "Пользователь с такой электронной почтой уже существует."
            flash("Не удалось создать учетную запись.", "error")

    return render_template("signup.html", errors=errors, form=form)


@bp.post("/logout")
def logout():
    logout_user()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("shop.home"))
