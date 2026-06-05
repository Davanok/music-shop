from decimal import Decimal, InvalidOperation

from flask import Flask

from .extensions import db
from .api import api as api_blueprint
from .config import Config
from .data.services import cart_count, cart_quantities, cart_totals, current_user
from .data.seeds import seed_data
from .ui import register_routes as register_ui_routes


def create_app(config_object=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_object)
    config_object.init_app(app)
    db.init_app(app)
    register_ui_routes(app)
    app.register_blueprint(api_blueprint)

    @app.cli.command("init-db")
    def init_db():
        """Create SQLAlchemy tables and load seed data."""
        db.create_all()
        seed_data()
        print("База данных Music Shop инициализирована.")

    @app.context_processor
    def inject_globals():
        return {
            "cart_count": cart_count(),
            "cart_quantities": cart_quantities(),
            "cart_totals": cart_totals,
            "current_user": current_user(),
        }

    @app.template_filter("currency")
    def currency(value):
        try:
            amount = Decimal(value or "0")
        except (InvalidOperation, TypeError, ValueError):
            amount = Decimal("0")
        return f"{amount:,.2f} ₽"

    return app
