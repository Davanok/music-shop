from flask import Flask

from .account import bp as account_bp
from .auth import bp as auth_bp
from .cart import bp as cart_bp
from .shop import bp as shop_bp
from .admin import register_routes as register_admin_routes


def register_routes(app: Flask):
    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(shop_bp)
    register_admin_routes(app)
