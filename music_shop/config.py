import os
from pathlib import Path


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-music-shop-secret")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "music_shop_dev")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "music_shop_password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "music_shop_dev")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    @staticmethod
    def init_app(app):
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
