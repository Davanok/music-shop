import pytest

from music_shop.app import create_app
from music_shop.data.services import cart_items, place_order
from music_shop.extensions import db
from music_shop.data.models import Category, Product, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "static/uploads"

    @staticmethod
    def init_app(app):
        pass


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_product():
    category = Category(
        slug="guitars",
        name="Гитары",
        description="Инструменты",
        image_url="https://example.com/category.jpg",
    )
    product = Product(
        slug="test-guitar",
        name="Тестовая гитара",
        category=category,
        description="Описание",
        price="100.00",
        stock=3,
        featured=True,
        image_url="https://example.com/product.jpg",
    )
    db.session.add_all([category, product])
    db.session.commit()
    return product


def create_user(email="customer@example.com", role="viewer"):
    user = User(
        email=email,
        name="Покупатель",
        password_hash="unused",
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_create_app():
    app = create_app(TestConfig)
    assert app is not None
    assert "music_shop" in app.name


def test_cart_items_ignores_malformed_session_entries(app):
    product = create_product()
    with app.test_request_context("/"):
        from flask import session

        session["cart"] = {str(product.id): "2", "bad-id": "5"}

        items = cart_items()

    assert len(items) == 1
    assert items[0]["product"].id == product.id
    assert items[0]["quantity"] == 2


def test_checkout_requires_authenticated_customer(client):
    create_product()
    with client.session_transaction() as session:
        session["cart"] = {"1": 1}

    response = client.get("/checkout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_place_order_creates_address_and_reduces_stock(app):
    product = create_product()
    user = create_user()

    with app.test_request_context("/"):
        from flask import session

        session["cart"] = {str(product.id): 2}
        order = place_order(
            user.name,
            user.email,
            {
                "country": "Россия",
                "city": "Москва",
                "street": "Тверская 1",
                "postal_code": "101000",
            },
        )

    assert order.address.city == "Москва"
    assert order.total == product.price * 2 + order.shipping
    assert db.session.get(Product, product.id).stock == 1


def test_catalog_page_shows_product_quantity_in_cart(client):
    product = create_product()
    with client.session_transaction() as session:
        session["cart"] = {str(product.id): 2}

    response = client.get("/catalog")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Все музыкальные товары" in html
    assert "cart-product-quantity" in html
    assert ">\n            2\n          </span>" in html


def test_checkout_allows_admin_user(client):
    product = create_product()
    admin = create_user("admin@example.com", "admin")
    with client.session_transaction() as session:
        session["user_id"] = admin.id
        session["cart"] = {str(product.id): 1}

    response = client.get("/checkout")

    assert response.status_code == 200
    assert "Разместить заказ" in response.get_data(as_text=True)


def test_signup_marks_invalid_fields(client):
    response = client.post(
        "/signup",
        data={"name": "", "email": "bad-email", "password": "123"},
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "field-error" in html
    assert "Введите имя." in html
    assert "Введите корректный адрес электронной почты." in html
    assert "Пароль должен содержать минимум 8 символов." in html
