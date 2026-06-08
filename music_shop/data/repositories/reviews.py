from ..database import db
from ..models import Review


def list_reviews_by_product(product_id):
    return Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()


def get_average_rating(product_id):
    from sqlalchemy import func
    result = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    return round(float(result), 1) if result else 0.0


def get_review_count(product_id):
    return Review.query.filter_by(product_id=product_id).count()


def save_review(review):
    db.session.add(review)
    db.session.commit()
    return review


def list_reviews():
    return Review.query.order_by(Review.created_at.desc()).all()


def get_review(review_id):
    return Review.query.get(review_id)


def delete_review(review_id):
    review = Review.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
    return review

