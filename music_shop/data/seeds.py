import json
from decimal import Decimal

from .database import db
from .models import AppSetting, Category, Product, User
from .services import DEFAULT_IMAGE, hash_password

SEED_CATEGORIES = [
    ("guitars", "Гитары", "Электрогитары, акустические и бас-гитары для сцены и студии.", "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80"),
    ("drums", "Барабаны", "Ударные установки, малые барабаны, тарелки и перкуссия.", "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80"),
    ("keyboards", "Клавишные", "Сценические пианино, синтезаторы, MIDI-контроллеры и рабочие станции.", "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80"),
    ("wind-instruments", "Духовые инструменты", "Саксофоны, трубы, флейты, кларнеты и другие духовые инструменты.", "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"),
    ("parts-accessories", "Запчасти и аксессуары", "Струны, палочки, чехлы, кабели, педали, трости и стойки.", "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80"),
]

SEED_PRODUCTS = [
    ("aurora-strat", "Электрогитара Aurora S-Style", "guitars", "Универсальная электрогитара с корпусом из ольхи, чистым звучанием, выразительным бриджем и сатинированным кленовым грифом.", Decimal("749.00"), 8, True, "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80"),
    ("studio-drum-kit", "Барабанная установка Studio Maple 5", "drums", "Теплые кленовые корпуса, надежная фурнитура и гибкая настройка резонанса для записи и концертов.", Decimal("1299.00"), 4, True, "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80"),
    ("nova-stage-88", "Клавишные Nova Stage 88", "keyboards", "Взвешенная клавиатура, выразительные тембры электропиано, разделение зон и USB MIDI для современной сцены.", Decimal("1599.00"), 5, True, "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80"),
    ("brassline-trumpet", "Труба Brassline Bb", "wind-instruments", "Яркая и отзывчивая труба с нержавеющими пистонами, точной интонацией и защитным футляром.", Decimal("629.00"), 0, False, "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"),
    ("tour-cable-pack", "Туровый набор кабелей и аксессуаров", "parts-accessories", "Набор для концертов: инструментальные и патч-кабели, медиаторы, тюнер, салфетка и стяжки.", Decimal("119.00"), 22, False, "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80"),
]


def seed_data():
    categories = {}
    for slug, name, description, image_url in SEED_CATEGORIES:
        category = Category.query.filter_by(slug=slug).one_or_none() or Category(slug=slug)
        category.name = name
        category.description = description
        category.image_url = image_url or DEFAULT_IMAGE
        db.session.add(category)
        categories[slug] = category
    db.session.flush()

    for slug, name, category_slug, description, price, stock, featured, image_url in SEED_PRODUCTS:
        product = Product.query.filter_by(slug=slug).one_or_none() or Product(slug=slug)
        product.name = name
        product.category = categories[category_slug]
        product.description = description
        product.price = price
        product.stock = stock
        product.featured = featured
        product.image_url = image_url
        product.gallery_json = json.dumps([image_url])
        db.session.add(product)

    setting = AppSetting.query.filter_by(key="delivery_price").one_or_none() or AppSetting(key="delivery_price")
    setting.value = "500.00"
    db.session.add(setting)

    if not User.query.filter_by(email="admin@music-shop.local").one_or_none():
        db.session.add(
            User(
                email="admin@music-shop.local",
                name="Главный администратор",
                password_hash=hash_password("admin12345"),
                role="admin",
            )
        )
    db.session.commit()
