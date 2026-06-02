import pytest
from music_shop.app import create_app

def test_create_app():
    app = create_app()
    assert app is not None
    assert "music_shop" in app.name