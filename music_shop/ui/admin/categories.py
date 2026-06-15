from flask import Blueprint, flash, redirect, request, url_for
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
        return redirect(url_for("admin.dashboard.index", section="categories", entry_id=category.id))
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")
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
    except IntegrityError:
        db.session.rollback()
        flash("Адрес категории должен быть уникальным.", "error")
    return redirect(url_for("admin.dashboard.index", section="categories", entry_id=category_id))


@bp.post("/<int:category_id>/delete")
@manager_required
def delete(category_id):
    try:
        repo.delete_category(category_id)
        flash("Категория удалена.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Нельзя удалить категорию, пока в ней есть товары.", "error")
    return redirect(url_for("admin.dashboard.index", section="categories"))