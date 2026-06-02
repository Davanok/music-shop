from sqlalchemy import select

from music_shop.data import db
from music_shop.data.models import Address


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