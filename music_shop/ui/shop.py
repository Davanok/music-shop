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


@bp.route("/products/<slug>")
def details(slug):
    product = repo.get_product_by_slug(slug)
    if not product:
        flash("Товар не найден.", "error")
        return redirect(url_for("shop.home"))
    return render_template("product_detail.html", product=product, gallery=product_gallery(product))


def _active_trail(slug: str) -> set[str]:
    """Slugs of selected category + all its ancestors."""
    if not slug or slug == "all":
        return set()
    cat = repo.get_category_by_slug(slug)
    if not cat:
        return set()
    return {c.slug for c in cat.breadcrumb}  # breadcrumb from model helper


@bp.route("/catalog")
def catalog():
    filters = get_filters()
    roots = repo.list_categories(root_only=True)
    return render_template(
        "catalog.html",
        categories=roots,                          # only roots; children via .children
        active_trail=_active_trail(filters["category"]),
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"]
        ),
        filters=filters,
    )


@bp.route("/catalog/products")
def catalog_products():
    filters = get_filters()
    roots = repo.list_categories(root_only=True)
    return render_template(
        "partials/product_grid.html",
        products=repo.list_products(
            search=filters["q"],
            category_slug=filters["category"],
            stock=filters["stock"]
        ),
        # pass these too if your partial renders filters
        categories=roots,
        active_trail=_active_trail(filters["category"]),
        filters=filters,
    )
