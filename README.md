# Music Shop

Modern music instruments e-commerce platform built with Flask + MySQL.

## Quick Start

```bash
git clone https://github.com/Davanok/music-shop.git
cd music-shop

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Run development server
python run.py
```

## Structure

- `music_shop/` - Main application package
- `templates/` - Jinja2 templates
- `static/` - Static assets
- `tests/` - Test suite

## Commands

- `flask --app music_shop.app init-db` - Initialize database