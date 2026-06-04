from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from music_shop.data import db
from music_shop.data.models import Order, OrderItem, User


def get_order_by_number(order_number: str):
    return db.session.scalars(
        select(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.address),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .where(Order.order_number == order_number)
    ).unique().first()


def list_orders_for_email(email: str):
    return db.session.scalars(
        select(Order)
        .join(Order.user)
        .options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .where(User.email == email)
        .order_by(Order.created_at.desc())
    ).unique().all()


def list_orders():
    return db.session.scalars(
        select(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .order_by(Order.created_at.desc())
    ).unique().all()


def total_revenue():
    order_totals = (
        select(
            (
                Order.shipping
                + func.coalesce(func.sum(OrderItem.unit_price * OrderItem.quantity), 0)
            ).label("total")
        )
        .outerjoin(Order.items)
        .group_by(Order.id)
        .subquery()
    )

    return db.session.scalar(
        select(func.coalesce(func.sum(order_totals.c.total), 0))
    )


def get_order(order_id: int):
    return db.session.scalars(
        select(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.address),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .where(Order.id == order_id)
    ).unique().first()


def update_order_status(order_id: int, status):
    order = get_order(order_id)
    if order:
        order.status = status
        db.session.commit()
    return order
