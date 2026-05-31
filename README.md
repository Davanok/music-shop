# Music Shop Flask + MySQL

A responsive music shop web application built with Python Flask and MySQL. It includes a storefront catalog, product details, cart, checkout, account order lookup, and an admin dashboard for products, categories, orders, and uploaded product images.

## Features

- Product catalog with category, stock, and text search filters.
- Product detail pages with gallery images, descriptions, prices, stock status, and add-to-cart forms.
- Session-backed shopping cart with quantity management and an order summary.
- Checkout flow that creates customers, orders, order items, and reduces stock in MySQL.
- Account page that shows order history by customer email.
- Admin dashboard for products, categories, revenue/order visibility, and product image uploads stored under `static/uploads`.
- Responsive HTML/CSS templates rendered by Flask.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create the MySQL database and user, then load schema and seed data:

   ```sql
   CREATE DATABASE music_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'music_shop'@'localhost' IDENTIFIED BY 'music_shop_password';
   GRANT ALL PRIVILEGES ON music_shop.* TO 'music_shop'@'localhost';
   FLUSH PRIVILEGES;
   ```

   ```bash
   mysql -u music_shop -p music_shop < schema.sql
   mysql -u music_shop -p music_shop < seed.sql
   ```

3. Configure environment variables as needed. `.env.example` lists supported values.

4. Run the app:

   ```bash
   flask --app app run --debug
   ```

5. Open `http://127.0.0.1:5000`.
