import json
from decimal import Decimal

from .database import db
from .models import AppSetting, Category, Product, User
from .services import DEFAULT_IMAGE, hash_password

SEED_CATEGORIES = [
    # (slug, name, description, image_url, parent_slug)
    # ── Root categories ──────────────────────────────────────────────────────
    ("guitars",           "Гитары",                  "Электрогитары, акустические и бас-гитары для сцены и студии.",              "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80", None),
    ("drums",             "Барабаны",                "Ударные установки, малые барабаны, тарелки и перкуссия.",                   "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", None),
    ("keyboards",         "Клавишные",               "Сценические пианино, синтезаторы, MIDI-контроллеры и рабочие станции.",     "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", None),
    ("wind-instruments",  "Духовые инструменты",     "Саксофоны, трубы, флейты, кларнеты и другие духовые инструменты.",         "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", None),
    ("parts-accessories", "Запчасти и аксессуары",   "Струны, палочки, чехлы, кабели, педали, трости и стойки.",                 "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", None),

    # ── Guitars ──────────────────────────────────────────────────────────────
    ("electric-guitars",  "Электрогитары",           "Solid-body, полуакустика и арchtop для любого стиля.",                     "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("acoustic-guitars",  "Акустические гитары",     "Дредноуты, концертные и джамбо для живого звука без усилителя.",           "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("bass-guitars",      "Бас-гитары",              "4- и 5-струнные бас-гитары для сцены и студии.",                           "https://images.unsplash.com/photo-1558098329-a11cff621064?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("guitar-amps",       "Усилители для гитары",    "Ламповые, транзисторные и моделирующие комбо и головы.",                   "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?auto=format&fit=crop&w=900&q=80", "guitars"),

    # ── Drums ─────────────────────────────────────────────────────────────────
    ("acoustic-drums",    "Акустические ударные",    "Кленовые, берёзовые и дубовые установки для студии и сцены.",              "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80", "drums"),
    ("electronic-drums",  "Электронные ударные",     "Компактные пэд-установки и модули для тихой практики и записи.",           "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),
    ("cymbals",           "Тарелки",                 "Хай-хэты, крэши, райды и сплэши ведущих брендов.",                        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),
    ("percussion",        "Перкуссия",               "Кахоны, конги, бонго, шейкеры и маракасы.",                               "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),

    # ── Keyboards ────────────────────────────────────────────────────────────
    ("synthesizers",      "Синтезаторы",             "Аналоговые, цифровые и виртуально-аналоговые синтезаторы.",               "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80", "keyboards"),
    ("digital-pianos",    "Цифровые пианино",        "Взвешенные клавиатуры с молоточковой механикой для дома и сцены.",         "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", "keyboards"),
    ("midi-controllers",  "MIDI-контроллеры",        "Клавишные, пэд- и смешанные контроллеры для DAW и живых выступлений.",     "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", "keyboards"),

    # ── Wind instruments ─────────────────────────────────────────────────────
    ("brass",             "Медные духовые",          "Трубы, тромбоны, валторны и тубы.",                                       "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", "wind-instruments"),
    ("woodwinds",         "Деревянные духовые",      "Саксофоны, кларнеты, флейты и гобои.",                                    "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", "wind-instruments"),

    # ── Parts & accessories ───────────────────────────────────────────────────
    ("strings-picks",     "Струны и медиаторы",      "Никелевые, стальные и нейлоновые струны, медиаторы всех форм и толщин.",   "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("cases-bags",        "Чехлы и кейсы",           "Гигбэги, твёрдые кейсы и рэковые сумки для любых инструментов.",          "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("cables-connectors", "Кабели и коннекторы",     "Инструментальные, балансные, MIDI и патч-кабели.",                        "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("stands-mounts",     "Стойки и крепления",      "Стойки для гитар, микрофонов, клавишных и ударных.",                      "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("effects-pedals",    "Эффекты и педали",        "Дисторшн, хорус, дилэй, лупер и мультиэффекты.",                          "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
]

SEED_PRODUCTS = [
    # (slug, name, category_slug, description, price, stock, featured, image_url)
    ("aurora-strat",      "Электрогитара Aurora S-Style",        "electric-guitars",  "Универсальная электрогитара с корпусом из ольхи, чистым звучанием и сатинированным кленовым грифом.",    Decimal("749.00"),  8,  True,  "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80"),
    ("studio-drum-kit",   "Барабанная установка Studio Maple 5", "acoustic-drums",    "Теплые кленовые корпуса и гибкая настройка резонанса для записи и концертов.",                           Decimal("1299.00"), 4,  True,  "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80"),
    ("nova-stage-88",     "Клавишные Nova Stage 88",             "digital-pianos",    "Взвешенная клавиатура, тембры электропиано, разделение зон и USB MIDI для современной сцены.",            Decimal("1599.00"), 5,  True,  "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80"),
    ("brassline-trumpet", "Труба Brassline Bb",                  "brass",             "Яркая и отзывчивая труба с нержавеющими пистонами, точной интонацией и защитным футляром.",              Decimal("629.00"),  0,  False, "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"),
    ("tour-cable-pack",   "Туровый набор кабелей и аксессуаров", "cables-connectors", "Набор для концертов: инструментальные и патч-кабели, медиаторы, тюнер, салфетка и стяжки.",             Decimal("119.00"),  22, False, "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80"),
]


def seed_data():
    # ── 1. Categories (two-pass: roots first, then children) ─────────────────
    categories: dict[str, Category] = {}

    for pass_no in range(2):
        for slug, name, description, image_url, parent_slug in SEED_CATEGORIES:
            is_root = parent_slug is None
            if (pass_no == 0) != is_root:   # pass 0 → roots; pass 1 → children
                continue

            category = Category.query.filter_by(slug=slug).one_or_none() or Category(slug=slug)
            category.name        = name
            category.description = description
            category.image_url   = image_url or DEFAULT_IMAGE
            category.parent      = categories[parent_slug] if parent_slug else None
            db.session.add(category)
            categories[slug] = category

        db.session.flush()   # assigns IDs after each pass so children can reference parents

    # ── 2. Products ───────────────────────────────────────────────────────────
    for slug, name, category_slug, description, price, stock, featured, image_url in SEED_PRODUCTS:
        product = Product.query.filter_by(slug=slug).one_or_none() or Product(slug=slug)
        product.name         = name
        product.category     = categories[category_slug]
        product.description  = description
        product.price        = price
        product.stock        = stock
        product.featured     = featured
        product.image_url    = image_url
        product.gallery_json = json.dumps([image_url])
        db.session.add(product)

    # ── 3. Settings & admin user ──────────────────────────────────────────────
    delivery_setting = AppSetting.query.filter_by(key="delivery_price").one_or_none() or AppSetting(key="delivery_price")
    delivery_setting.value = "500.00"
    db.session.add(delivery_setting)

    assembly_setting = AppSetting.query.filter_by(key="assembly_price").one_or_none() or AppSetting(key="assembly_price")
    assembly_setting.value = "1000.00"
    db.session.add(assembly_setting)

    if not User.query.filter_by(email="admin@music-shop.local").one_or_none():
        db.session.add(User(
            email="admin@music-shop.local",
            name="Главный администратор",
            password_hash=hash_password("admin12345"),
            role="admin",
        ))

    if not User.query.filter_by(email="manager@music-shop.local").one_or_none():
        db.session.add(User(
            email="manager@music-shop.local",
            name="Менеджер магазина",
            password_hash=hash_password("manager12345"),
            role="manager",
        ))

    if not User.query.filter_by(email="user@music-shop.local").one_or_none():
        db.session.add(User(
            email="user@music-shop.local",
            name="Обычный пользователь",
            password_hash=hash_password("user12345"),
            role="user",
        ))

    db.session.commit()
