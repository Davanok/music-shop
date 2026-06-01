from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload

from .database import db
from .models import (
    AppSetting,
    Address,
    Category,
    Order,
    OrderStatus,
    Product,
    User,
)


# -------------------------
# CATEGORIES
# -------------------------

def list_categories():
    return db.session.scalars(
        select(Category).order_by(Category.name)
    ).all()


def get_category(category_id: int):
    return db.session.get(Category, category_id)


def create_category(slug, name, description, image_url):
    category = Category(
        slug=slug,
        name=name,
        description=description,
        image_url=image_url,
    )
    db.session.add(category)
    db.session.commit()
    return category


def delete_category(category_id: int):
    category = get_category(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()


# -------------------------
# PRODUCTS
# -------------------------

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


# -------------------------
# USERS
# -------------------------

def list_users():
    return db.session.scalars(
        select(User).order_by(User.role, User.email)
    ).all()


def get_user(user_id: int):
    return db.session.get(User, user_id)


def get_user_by_email(email: str):
    return db.session.scalar(
        select(User).where(User.email == email)
    )


def create_user(email, name, password_hash, role="customer"):
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user

def update_user_role(user_id: int, role: str):
    user = get_user(user_id)
    if user:
        user.role = role
        db.session.commit()
    return user


# -------------------------
# ADDRESSES
# -------------------------

def list_addresses_for_user(user_id: int):
    return db.session.scalars(
        select(Address)
        .where(Address.user_id == user_id)
    ).all()


def create_address(user_id, country, city, street, postal_code):
    address = Address(
        user_id=user_id,
        country=country,
        city=city,
        street=street,
        postal_code=postal_code,
    )
    db.session.add(address)
    db.session.commit()
    return address


# -------------------------
# ORDERS
# -------------------------

def get_order_by_number(order_number: str):
    return db.session.scalars(
        select(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.address),
            joinedload(Order.status),
            joinedload(Order.items),
        )
        .where(Order.order_number == order_number)
    ).unique().first()


def list_orders_for_email(email: str):
    return db.session.scalars(
        select(Order)
        .join(Order.user)
        .options(joinedload(Order.user))
        .where(User.email == email)
        .order_by(Order.created_at.desc())
    ).unique().all()


def list_orders():
    return db.session.scalars(
        select(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.status),
        )
        .order_by(Order.created_at.desc())
    ).unique().all()


def total_revenue():
    return db.session.scalar(
        select(func.coalesce(func.sum(Order.shipping), 0))
    )


# -------------------------
# SETTINGS
# -------------------------

def get_setting(key, default=None):
    setting = db.session.scalar(
        select(AppSetting).where(AppSetting.key == key)
    )
    return setting.value if setting else default


def set_setting(key, value):
    setting = (
        db.session.scalar(
            select(AppSetting).where(AppSetting.key == key)
        )
        or AppSetting(key=key)
    )

    setting.value = str(value)
    db.session.add(setting)
    db.session.commit()
    return setting