from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload

from .database import db
from .models import Category, Customer, Order, Product


def list_categories():
    return db.session.scalars(select(Category).order_by(Category.name)).all()


def get_category(category_id):
    return db.session.get(Category, category_id)


def create_category(slug, name, description, image_url):
    category = Category(slug=slug, name=name, description=description, image_url=image_url)
    db.session.add(category)
    db.session.commit()
    return category


def delete_category(category_id):
    category = get_category(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()


def product_query():
    return select(Product).options(joinedload(Product.category))


def list_products(search="", category_slug="all", stock="all", featured_only=False, limit=None):
    statement: Select = product_query()
    if featured_only:
        statement = statement.where(Product.featured.is_(True))
    if search:
        term = f"%{search}%"
        statement = statement.where((Product.name.like(term)) | (Product.description.like(term)))
    if category_slug != "all":
        statement = statement.join(Product.category).where(Category.slug == category_slug)
    if stock == "in-stock":
        statement = statement.where(Product.stock > 0)
    elif stock == "out-of-stock":
        statement = statement.where(Product.stock == 0)
    statement = statement.order_by(Product.featured.desc(), Product.name)
    if limit:
        statement = statement.limit(limit)
    return db.session.scalars(statement).unique().all()


def get_product(product_id):
    return db.session.get(Product, product_id)


def get_product_by_slug(slug):
    return db.session.scalars(product_query().where(Product.slug == slug)).first()


def list_products_by_ids(product_ids):
    if not product_ids:
        return []
    return db.session.scalars(product_query().where(Product.id.in_(product_ids)).order_by(Product.name)).unique().all()


def save_product(product=None, **payload):
    product = product or Product()
    for key, value in payload.items():
        setattr(product, key, value)
    db.session.add(product)
    db.session.commit()
    return product


def delete_product(product_id):
    product = get_product(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()


def get_or_create_customer(name, email, address):
    customer = db.session.scalar(select(Customer).where(Customer.email == email))
    if customer:
        customer.name = name
        customer.address = address
    else:
        customer = Customer(name=name, email=email, address=address)
        db.session.add(customer)
    db.session.flush()
    return customer


def save_order(order):
    db.session.add(order)
    db.session.commit()
    return order


def get_order_by_number(order_number):
    return db.session.scalars(
        select(Order).options(joinedload(Order.customer), joinedload(Order.items)).where(Order.order_number == order_number)
    ).unique().first()


def list_orders_for_email(email):
    return db.session.scalars(
        select(Order).join(Order.customer).options(joinedload(Order.customer)).where(Customer.email == email).order_by(Order.created_at.desc())
    ).unique().all()


def list_orders():
    return db.session.scalars(select(Order).options(joinedload(Order.customer)).order_by(Order.created_at.desc())).unique().all()


def total_revenue():
    return db.session.scalar(select(func.coalesce(func.sum(Order.total), 0)))


__all__ = [
    "create_category",
    "delete_category",
    "delete_product",
    "get_category",
    "get_order_by_number",
    "get_or_create_customer",
    "get_product",
    "get_product_by_slug",
    "list_categories",
    "list_orders",
    "list_orders_for_email",
    "list_products",
    "list_products_by_ids",
    "save_order",
    "save_product",
    "total_revenue",
]
