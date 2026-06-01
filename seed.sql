INSERT INTO categories (slug, name, description, image_url) VALUES
('guitars', 'Гитары', 'Электрогитары, акустические и бас-гитары для сцены и студии.', 'https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80'),
('drums', 'Барабаны', 'Ударные установки, малые барабаны, тарелки и перкуссия.', 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80'),
('keyboards', 'Клавишные', 'Сценические пианино, синтезаторы, MIDI-контроллеры и рабочие станции.', 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80'),
('wind-instruments', 'Духовые инструменты', 'Саксофоны, трубы, флейты, кларнеты и другие духовые инструменты.', 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80'),
('parts-accessories', 'Запчасти и аксессуары', 'Струны, палочки, чехлы, кабели, педали, трости и стойки.', 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), image_url = VALUES(image_url);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'aurora-strat', 'Электрогитара Aurora S-Style', id, 'Универсальная электрогитара с корпусом из ольхи, чистым звучанием и сатинированным кленовым грифом.', 749.00, 8, TRUE, 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'guitars'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'studio-drum-kit', 'Барабанная установка Studio Maple 5', id, 'Теплые кленовые корпуса, надежная фурнитура и гибкая настройка резонанса.', 1299.00, 4, TRUE, 'https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'drums'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO users (email, name, password_hash, role) VALUES
('admin@music-shop.local', 'Главный администратор', 'pbkdf2:sha256:1000000$musicshopsalt$8358d72fb9e73560c4c57a2f1f0b549f42351139a59f99823802b4ed12623e7e', 'admin')
ON DUPLICATE KEY UPDATE name = VALUES(name), role = VALUES(role);

INSERT INTO app_settings (`key`, value) VALUES ('delivery_price', '500.00')
ON DUPLICATE KEY UPDATE value = VALUES(value);
