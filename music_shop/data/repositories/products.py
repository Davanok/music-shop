from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from music_shop.data.database import db
from music_shop.data.models import Category, Product


def product_query():
    return select(Product).options(joinedload(Product.category))


def list_products(
    search="",
    category_slug="all",
    stock="all",
    featured_only=False,
    limit=None,
):
    statement: Select = product_query()

    if featured_only:
        statement = statement.where(Product.featured.is_(True))

    if search:
        term = f"%{search}%"
        statement = statement.where(
            (Product.name.like(term)) |
            (Product.description.like(term))
        )

    if category_slug != "all":
        statement = statement.join(Product.category).where(
            Category.slug == category_slug
        )

    if stock == "in-stock":
        statement = statement.where(Product.stock > 0)
    elif stock == "out-of-stock":
        statement = statement.where(Product.stock == 0)

    statement = statement.order_by(
        Product.featured.desc(),
        Product.name,
    )

    if limit:
        statement = statement.limit(limit)

    return db.session.scalars(statement).unique().all()


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