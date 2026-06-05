from flask import Flask, Blueprint

from .categories import bp as category_bp
from .dashboard import bp as dashboard_bp
from .orders import bp as orders_bp
from .products import bp as products_bp
from .users import bp as users_bp

admin = Blueprint("admin", __name__, url_prefix="/admin")

def register_routes(app: Flask):
    admin.register_blueprint(category_bp)
    admin.register_blueprint(dashboard_bp)
    admin.register_blueprint(orders_bp)
    admin.register_blueprint(products_bp)
    admin.register_blueprint(users_bp)

    app.register_blueprint(admin)
