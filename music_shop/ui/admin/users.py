from flask import flash, redirect, request, url_for, Blueprint, jsonify
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
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "user"
        user = repo.create_user(
            email=request.form["email"].strip().lower(),
            name=request.form["name"].strip(),
            password_hash=hash_password(request.form["password"]),
            role=role,
        )
        flash("Учетная запись создана.", "success")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="users",
                entry_id=user.id,
                success=True,
                message="Учетная запись создана"
            )

        return redirect(url_for("admin.dashboard.index", section="users", entry_id=user.id))
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="users",
                entry_id=None,
                success=False,
                message="Пользователь с такой электронной почтой уже существует"
            )

    return redirect(url_for("admin.dashboard.index", section="users", action="new"))


@bp.post("/<int:user_id>/edit")
@admin_required
def update(user_id):
    try:
        role = request.form["role"] if request.form["role"] in ROLE_LABELS else "user"
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

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="users",
                entry_id=user_id,
                success=True,
                message="Пользователь обновлен"
            )
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с такой электронной почтой уже существует.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="users",
                entry_id=user_id,
                success=False,
                message="Пользователь с такой электронной почтой уже существует"
            )

    return redirect(url_for("admin.dashboard.index", section="users", entry_id=user_id))


def _get_spa_response(section, entry_id, success, message):
    """Вспомогательная функция для формирования SPA ответов"""
    from flask import render_template

    users = repo.list_users()
    selected_user = repo.get_user(entry_id) if entry_id else None

    list_panel = render_template(
        "admin/partials/section_content.html",
        active_section=section,
        users=users,
        categories=repo.list_categories(),
        products=repo.list_products(),
        orders=repo.list_orders(),
        reviews=repo.list_reviews(),
        role_labels=ROLE_LABELS,
        selected_user=selected_user,
        selected_product=None,
        selected_category=None,
        selected_order=None,
        selected_review=None,
    )

    form_panel = render_template(
        "admin/partials/form_only.html",
        active_section=section,
        selected_user=selected_user,
        is_adding=entry_id is None,
        role_labels=ROLE_LABELS,
        categories=[],
        products=[],
        order_statuses=[]
    )

    return jsonify({
        "success": success,
        "message": message,
        "listPanel": list_panel,
        "formPanel": form_panel
    })