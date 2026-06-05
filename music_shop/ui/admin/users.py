from flask import flash, redirect, request, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import (
    ROLE_LABELS,
    admin_required,
    current_user,
    hash_password,
)

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.post("")
@admin_required
def create():
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
        user = repo.create_user(
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            password_hash=hash_password(request.form["password"]),
            role=role,
        )
        flash("Учетная запись создана.", "success")
        return redirect(url_for("admin.dashboard.index", section="users", entry_id=user.id))
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")
    return redirect(url_for("admin.dashboard.index", section="users", action="new"))


@bp.post("/<int:user_id>/edit")
@admin_required
def update(user_id):
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "viewer"
        if current_user() and user_id == current_user().id and role != "admin":
            role = "admin"
            flash("Нельзя снять роль администратора у своей учетной записи.", "error")
        password = request.form.get("password", "")
        password_hash = hash_password(password) if password else None
        repo.update_user(
            user_id,
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            role=role,
            password_hash=password_hash,
        )
        flash("Пользователь обновлен.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")
    return redirect(url_for("admin.dashboard.index", section="users", entry_id=user_id))
