from sqlalchemy import select

from music_shop.data.database import db
from music_shop.data.models import User


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


def update_user(user_id: int, email, name, role, password_hash=None):
    user = get_user(user_id)
    if user:
        user.email = email
        user.name = name
        user.role = role
        if password_hash:
            user.password_hash = password_hash
        db.session.commit()
    return user
