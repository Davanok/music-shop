import json
from decimal import Decimal

from .database import db
from .models import Category, Product
from .services import DEFAULT_IMAGE

SEED_CATEGORIES = [
    ("guitars", "Guitars", "Electric, acoustic, and bass guitars for every stage.", "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80"),
    ("drums", "Drums", "Kits, snares, cymbals, and percussion essentials.", "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80"),
    ("keyboards", "Keyboards", "Stage pianos, synths, MIDI controllers, and workstations.", "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80"),
    ("wind-instruments", "Wind Instruments", "Saxophones, trumpets, flutes, clarinets, and more.", "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"),
    ("parts-accessories", "Parts & Accessories", "Strings, sticks, cases, cables, pedals, reeds, and stands.", "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80"),
]

SEED_PRODUCTS = [
    ("aurora-strat", "Aurora S-Style Electric Guitar", "guitars", "A versatile alder-body electric guitar with glassy cleans, punchy bridge tones, and a satin maple neck built for long sessions.", Decimal("749.00"), 8, True, "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80"),
    ("studio-drum-kit", "Studio Maple 5-Piece Drum Kit", "drums", "Warm maple shells, road-ready hardware, and tunable resonance make this kit a reliable anchor for recording or touring.", Decimal("1299.00"), 4, True, "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80"),
    ("nova-stage-88", "Nova Stage 88 Keyboard", "keyboards", "Weighted keys, expressive electric piano patches, split/layer control, and USB MIDI for modern performance rigs.", Decimal("1599.00"), 5, True, "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80"),
    ("brassline-trumpet", "Brassline Bb Trumpet", "wind-instruments", "A bright, responsive trumpet with stainless pistons, balanced intonation, and a protective molded case.", Decimal("629.00"), 0, False, "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"),
    ("tour-cable-pack", "Tour Cable & Accessory Pack", "parts-accessories", "A gig-bag staple with instrument cables, patch cables, picks, a tuner, microfiber cloth, and cable ties.", Decimal("119.00"), 22, False, "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80"),
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
    db.session.commit()
