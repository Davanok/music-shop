from flask import request, Blueprint, flash, redirect, url_for, jsonify, render_template

from music_shop.data import repositories as repo
from music_shop.data.services import manager_required

bp = Blueprint("reviews", __name__)


@bp.post("/<int:review_id>/delete")
@manager_required
def delete_review(review_id):
    repo.delete_review(review_id)
    flash("Отзыв удален.", "success")

    # Для AJAX запросов
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _get_spa_response(
            section="reviews",
            entry_id=None,
            success=True,
            message="Отзыв удален"
        )

    return redirect(url_for("admin.dashboard.index", section="reviews"))


def _get_spa_response(section, entry_id, success, message):
    """Вспомогательная функция для формирования SPA ответов"""
    from flask import render_template

    reviews = repo.list_reviews()
    selected_review = repo.get_review(entry_id) if entry_id else None

    list_panel = render_template(
        "admin/partials/section_content.html",
        active_section=section,
        reviews=reviews,
        categories=repo.list_categories(),
        products=repo.list_products(),
        orders=repo.list_orders(),
        users=repo.list_users(),
        role_labels={},
        selected_review=selected_review,
        selected_product=None,
        selected_category=None,
        selected_user=None,
        selected_order=None,
    )

    form_panel = render_template(
        "admin/partials/form_only.html",
        active_section=section,
        selected_review=selected_review,
        is_adding=False,
        categories=[],
        products=[],
        role_labels={},
        order_statuses=[]
    )

    return jsonify({
        "success": success,
        "message": message,
        "listPanel": list_panel,
        "formPanel": form_panel
    })