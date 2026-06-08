from sqlalchemy import Select, select, or_
from sqlalchemy.orm import joinedload

from music_shop.data.database import db
from music_shop.data.models import Category, Product
from music_shop.data.repositories import get_category_by_slug
from music_shop.data.repositories.categories import _collect_category_ids


def product_query():
    return select(Product).options(joinedload(Product.category))


def list_products(
    search: str = "",
    category_slug: str = "all",
    stock: str = "all",
    featured_only: bool = False,
    limit: int | None = None,
):
    q = select(Product)

    # Full-text search
    if search:
        term = f"%{search}%"
        q = q.where(
            or_(Product.name.ilike(term), Product.description.ilike(term))
        )

    # Deep category filter — includes all descendants
    if category_slug and category_slug != "all":
        category = get_category_by_slug(category_slug)
        if category:
            ids = _collect_category_ids(category)
            q = q.where(Product.category_id.in_(ids))

    # Stock filter
    if stock == "in-stock":
        q = q.where(Product.stock > 0)
    elif stock == "out-of-stock":
        q = q.where(Product.stock == 0)

    if featured_only:
        q = q.where(Product.featured.is_(True))

    if limit:
        q = q.limit(limit)

    return db.session.scalars(q).all()


def get_product(product_id: int):
    return db.session.get(Product, product_id)


def get_product_by_slug(slug: str):
    return db.session.scalars(
        product_query().where(Product.slug == slug)
    ).first()


def list_products_by_ids(product_ids: list[int]):
    if not product_ids:
        return []

    return db.session.scalars(
        product_query()
        .where(Product.id.in_(product_ids))
        .order_by(Product.name)
    ).unique().all()


def save_product(product=None, **payload):
    product = product or Product()

    for key, value in payload.items():
        setattr(product, key, value)

    db.session.add(product)
    db.session.commit()
    return product


def delete_product(product_id: int):
    product = get_product(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()

def list_related_products(product: Product, limit: int = 4):
    q = select(Product).where(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(limit)
    return db.session.scalars(q).all()
