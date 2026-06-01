from decimal import Decimal

from flask import Flask

from .api.routes import api
from .config import Config
from .data.database import db
from .data.services import cart_count, cart_totals, current_user
from .data.seeds import seed_data
from .ui.routes import ui


def create_app(config_object=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_object)
    config_object.init_app(app)
    db.init_app(app)
    app.register_blueprint(ui)
    app.register_blueprint(api)


    @app.cli.command("init-db")
    def init_db():
        """Create SQLAlchemy tables and load seed data."""
        db.create_all()
        seed_data()
        print("База данных Music Shop инициализирована.")

    @app.context_processor
    def inject_globals():
        return {"cart_count": cart_count(), "cart_totals": cart_totals, "current_user": current_user()}

    @app.template_filter("currency")
    def currency(value):
        return f"{Decimal(value):,.2f}₽"

    return app
