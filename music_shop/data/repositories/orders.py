from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from music_shop.data import db
from music_shop.data.models import Order, User


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