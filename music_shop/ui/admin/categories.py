from flask import Blueprint, flash, redirect, request, url_for, jsonify
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import (
    DEFAULT_IMAGE,
    manager_required,
    slugify,
)

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.post("")
@manager_required
def add():
    try:
        name = request.form["name"].strip()
        category = repo.create_category(
            slug=slugify(request.form.get("slug") or name),
            name=name,
            description=request.form.get("description") or "Пользовательская категория.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Категория добавлена.", "success")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=category.id,
                success=True,
                message="Категория добавлена"
            )

        return redirect(url_for("admin.dashboard.index", section="categories", entry_id=category.id))
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=None,
                success=False,
                message="Адрес категории должен быть уникальным"
            )

    return redirect(url_for("admin.dashboard.index", section="categories", action="new"))


@bp.post("/<int:category_id>/edit")
@manager_required
def update(category_id):
    try:
        name = request.form["name"].strip()
        repo.update_category(
            category_id,
            slug=slugify(request.form.get("slug") or name),
            name=name,
            description=request.form.get("description") or "Пользовательская категория.",
            image_url=request.form.get("image_url") or DEFAULT_IMAGE,
        )
        flash("Категория обновлена.", "success")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=category_id,
                success=True,
                message="Категория обновлена"
            )
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=category_id,
                success=False,
                message="Адрес категории должен быть уникальным"
            )

    return redirect(url_for("admin.dashboard.index", section="categories", entry_id=category_id))


@bp.post("/<int:category_id>/delete")
@manager_required
def delete(category_id):
    try:
        repo.delete_category(category_id)
        flash("Категория удалена.", "success")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=None,
                success=True,
                message="Категория удалена"
            )
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить категорию, пока в ней есть товары.", "error")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _get_spa_response(
                section="categories",
                entry_id=category_id,
                success=False,
                message="Нельзя удалить категорию, пока в ней есть товары"
            )

    return redirect(url_for("admin.dashboard.index", section="categories"))


def _get_spa_response(section, entry_id, success, message):
    """Вспомогательная функция для формирования SPA ответов"""
    from flask import render_template

    # Получаем обновленные данные
    categories = repo.list_categories()
    selected_category = repo.get_category(entry_id) if entry_id else None

    # Рендерим обновленные панели
    list_panel = render_template(
        "admin/partials/section_content.html",
        active_section=section,
        categories=categories,
        products=repo.list_products(),
        orders=repo.list_orders(),
        users=repo.list_users(),
        reviews=repo.list_reviews(),
        role_labels={},
        selected_category=selected_category,
        selected_product=None,
        selected_user=None,
        selected_order=None,
        selected_review=None,
    )

    form_panel = render_template(
        "admin/partials/form_only.html",
        active_section=section,
        categories=categories,
        selected_category=selected_category,
        selected_product=None,
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