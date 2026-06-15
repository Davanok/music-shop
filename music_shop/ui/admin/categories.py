from flask import Blueprint, flash, redirect, request, url_for, render_template
from sqlalchemy.exc import IntegrityError

from music_shop.data import repositories as repo
from music_shop.data.database import db
from music_shop.data.services import (
    DEFAULT_IMAGE,
    manager_required,
    slugify,
    save_uploaded_image,
)

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/add", methods=["GET", "POST"])
@bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
@manager_required
def add_or_edit(category_id=None):
    selected_category = repo.get_category(category_id) if category_id else None

    if request.method == "POST":
        try:
            # Handle image upload
            uploaded_image = save_uploaded_image(request.files.get("image_file"))
            image_url = uploaded_image or request.form.get("image_url") or (
                selected_category.image_url if selected_category else None) or DEFAULT_IMAGE

            name = request.form["name"].strip()
            slug = slugify(request.form.get("slug") or name)
            description = request.form.get("description") or "Пользовательская категория."

            if selected_category:
                repo.update_category(
                    category_id,
                    slug=slug,
                    name=name,
                    description=description,
                    image_url=image_url,
                )
                flash("Категория обновлена.", "success")
            else:
                repo.create_category(
                    slug=slug,
                    name=name,
                    description=description,
                    image_url=image_url,
                )
                flash("Категория создана.", "success")

            return redirect(url_for("admin.dashboard.index", section="categories"))

        except IntegrityError:
            db.session.rollback()
            flash("Адрес категории должен быть уникальным.", "error")

    return render_template("admin/categories_form.html",
                           selected_category=selected_category,
                           is_adding=not selected_category)


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
