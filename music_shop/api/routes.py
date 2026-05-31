from flask import Blueprint, jsonify, request

from music_shop.data import repositories as repo
from music_shop.data.services import add_to_cart, cart_count, cart_items, cart_totals, to_product_dict

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/products")
def products():
    products = repo.list_products(
        search=request.args.get("q", "").strip(),
        category_slug=request.args.get("category", "all"),
        stock=request.args.get("stock", "all"),
    )
    return jsonify([to_product_dict(product) for product in products])


@api.get("/products/<slug>")
def product(slug):
    product = repo.get_product_by_slug(slug)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(to_product_dict(product))


@api.get("/categories")
def categories():
    return jsonify([
        {"id": category.id, "slug": category.slug, "name": category.name, "description": category.description, "image_url": category.image_url}
        for category in repo.list_categories()
    ])


@api.get("/cart")
def cart():
    items = cart_items()
    totals = cart_totals(items)
    return jsonify(
        {
            "count": cart_count(),
            "items": [
                {"product": to_product_dict(item["product"]), "quantity": item["quantity"], "line_total": str(item["line_total"])}
                for item in items
            ],
            "totals": {key: str(value) for key, value in totals.items()},
        }
    )


@api.post("/cart/items")
def add_cart_item():
    payload = request.get_json(silent=True) or request.form
    if not add_to_cart(int(payload["product_id"]), int(payload.get("quantity", 1))):
        return jsonify({"error": "Product is unavailable"}), 400
    return cart(), 201
