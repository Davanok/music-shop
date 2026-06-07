from sqlalchemy import select

from music_shop.data.database import db
from music_shop.data.models import Category

def _collect_category_ids(category: Category) -> list[int]:
    """Recursively collect a category's id + all descendant ids."""
    ids = [category.id]
    for child in category.children:
        ids.extend(_collect_category_ids(child))
    return ids

def list_categories(root_only: bool = False):
    """Return categories. root_only=True returns only top-level ones."""
    q = select(Category).order_by(Category.name)
    if root_only:
        q = q.where(Category.parent_id.is_(None))
    return db.session.scalars(q).all()


def get_category_by_slug(slug: str) -> Category | None:
    return db.session.scalar(
        select(Category).where(Category.slug == slug)
    )

def get_category(category_id: int):
    return db.session.get(Category, category_id)


def create_category(slug, name, description, image_url, parent_id=None):
    category = Category(
        slug=slug, name=name, description=description,
        image_url=image_url, parent_id=parent_id,
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category_id, slug, name, description, image_url, parent_id=None):
    category = get_category(category_id)
    if category:
        category.slug = slug
        category.name = name
        category.description = description
        category.image_url = image_url
        category.parent_id = parent_id
        db.session.commit()
    return category


def delete_category(category_id: int):
    category = get_category(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()