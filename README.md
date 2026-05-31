# Music Shop Flask + MySQL

A responsive music shop web application built with Python Flask, SQLAlchemy, and MySQL. It includes a storefront catalog, product details, cart, checkout, account order lookup, JSON API endpoints, and an admin dashboard for products, categories, orders, and uploaded product images.

## Architecture

The app is split into explicit layers:

- `music_shop/ui/` contains browser-facing Flask routes that render Jinja templates.
- `music_shop/api/` contains JSON API routes under `/api` for products, categories, and cart operations.
- `music_shop/data/` contains SQLAlchemy setup, ORM models, repositories, and service functions for cart, checkout, uploads, and serialization.
- `templates/` contains the UI layer templates, and `static/` contains CSS plus uploaded product images.

## Features

- Product catalog with category, stock, and text search filters.
- Product detail pages with gallery images, descriptions, prices, stock status, and add-to-cart forms.
- Session-backed shopping cart with quantity management and an order summary.
- Checkout flow that creates customers, orders, order items, and reduces stock in MySQL through SQLAlchemy transactions.
- Account page that shows order history by customer email.
- Admin dashboard for products, categories, revenue/order visibility, and product image uploads stored under `static/uploads`.
- JSON API endpoints for catalog/category/cart integrations.
- Responsive HTML/CSS templates rendered by Flask.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create the MySQL database and user:

   ```sql
   CREATE DATABASE music_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'music_shop'@'localhost' IDENTIFIED BY 'music_shop_password';
   GRANT ALL PRIVILEGES ON music_shop.* TO 'music_shop'@'localhost';
   FLUSH PRIVILEGES;
   ```


3. Configure environment variables as needed. `.env.example` lists supported values, including `DATABASE_URL` for overriding the default SQLAlchemy MySQL connection string.

4. Create SQLAlchemy tables and load seed data:

   ```bash
   flask --app app init-db
   ```

   The legacy `schema.sql` and `seed.sql` files are also included for teams that prefer direct MySQL imports.

5. Run the app:

   ```bash
   flask --app app run --debug
   ```

6. Open `http://127.0.0.1:5000`.

## API examples

- `GET /api/products?q=guitar&category=guitars&stock=in-stock`
- `GET /api/products/aurora-strat`
- `GET /api/categories`
- `GET /api/cart`
- `POST /api/cart/items` with JSON like `{ "product_id": 1, "quantity": 2 }`
