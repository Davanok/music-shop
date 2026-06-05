from flask import Blueprint, flash, redirect, render_template, url_for
from flask import request

from music_shop.data import repositories as repo
from music_shop.data.services import product_gallery


def get_filters():
    return {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "all"),
        "stock": request.args.get("stock", "all"),
    }


bp = Blueprint("shop", __name__)


@bp.route("/")
def home():
    return render_template(
        "home.html",
        categories=repo.list_categories(),
        featured=repo.list_products(featured_only=True, limit=3),
    )


@bp.route("/catalog")
def catalog():
    filters = get_filters()

    return render_template(
        "catalog.html",
        categories=repo.list_categories(),
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"],
        ),
        filters=filters,
    )


@bp.route("/catalog/products")
def catalog_products():
    filters = get_filters()

    return render_template(
        "partials/product_grid.html",
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"],
        ),
    )


@bp.route("/products/<slug>")
def details(slug):
    product = repo.get_product_by_slug(slug)
    if not product:
        flash("Товар не найден.", "error")
        return redirect(url_for("shop.home"))
    return render_template("product_detail.html", product=product, gallery=product_gallery(product))
