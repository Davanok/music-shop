from flask import Blueprint, jsonify, request

from music_shop.data import repositories as repo
from music_shop.data.services import add_to_cart, cart_payload, remove_from_cart, set_cart_quantity, to_product_dict

api = Blueprint("api", __name__, url_prefix="/api")


def read_quantity(default=1):
    payload = request.get_json(silent=True) or request.form
    try:
        return int(payload.get("quantity", default))
    except (TypeError, ValueError):
        return default


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
        return jsonify({"error": "Товар не найден"}), 404
    return jsonify(to_product_dict(product))


@api.get("/categories")
def categories():
    return jsonify([
        {"id": category.id, "slug": category.slug, "name": category.name, "description": category.description, "image_url": category.image_url}
        for category in repo.list_categories()
    ])


@api.get("/cart")
def cart():
    return jsonify(cart_payload())


@api.post("/cart/items")
def add_cart_item():
    payload = request.get_json(silent=True) or request.form
    try:
        product_id = int(payload["product_id"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Некорректный товар"}), 400
    if not add_to_cart(product_id, read_quantity()):
        return jsonify({"error": "Товар недоступен"}), 400
    return jsonify(cart_payload()), 201


@api.patch("/cart/items/<int:product_id>")
def update_cart_item(product_id):
    set_cart_quantity(product_id, read_quantity(default=0))
    return jsonify(cart_payload())


@api.delete("/cart/items/<int:product_id>")
def delete_cart_item(product_id):
    remove_from_cart(product_id)
    return jsonify(cart_payload())
