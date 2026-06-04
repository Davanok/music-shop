from sqlalchemy import select

from music_shop.data.database import db
from music_shop.data.models import Category


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


def update_category(category_id: int, slug, name, description, image_url):
    category = get_category(category_id)
    if category:
        category.slug = slug
        category.name = name
        category.description = description
        category.image_url = image_url
        db.session.commit()
    return category
