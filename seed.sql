INSERT INTO categories (slug, name, description, image_url) VALUES
('guitars', 'Guitars', 'Electric, acoustic, and bass guitars for every stage.', 'https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80'),
('drums', 'Drums', 'Kits, snares, cymbals, and percussion essentials.', 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80'),
('keyboards', 'Keyboards', 'Stage pianos, synths, MIDI controllers, and workstations.', 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80'),
('wind-instruments', 'Wind Instruments', 'Saxophones, trumpets, flutes, clarinets, and more.', 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80'),
('parts-accessories', 'Parts & Accessories', 'Strings, sticks, cases, cables, pedals, reeds, and stands.', 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), image_url = VALUES(image_url);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'aurora-strat', 'Aurora S-Style Electric Guitar', id, 'A versatile alder-body electric guitar with glassy cleans, punchy bridge tones, and a satin maple neck built for long sessions.', 749.00, 8, TRUE, 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80', 'https://images.unsplash.com/photo-1550291652-6ea9114a47b1?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'guitars'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'studio-drum-kit', 'Studio Maple 5-Piece Drum Kit', id, 'Warm maple shells, road-ready hardware, and tunable resonance make this kit a reliable anchor for recording or touring.', 1299.00, 4, TRUE, 'https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'drums'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'nova-stage-88', 'Nova Stage 88 Keyboard', id, 'Weighted keys, expressive electric piano patches, split/layer control, and USB MIDI for modern performance rigs.', 1599.00, 5, TRUE, 'https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'keyboards'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'brassline-trumpet', 'Brassline Bb Trumpet', id, 'A bright, responsive trumpet with stainless pistons, balanced intonation, and a protective molded case.', 629.00, 0, FALSE, 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'wind-instruments'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);

INSERT INTO products (slug, name, category_id, description, price, stock, featured, image_url, gallery_json)
SELECT 'tour-cable-pack', 'Tour Cable & Accessory Pack', id, 'A gig-bag staple with instrument cables, patch cables, picks, a tuner, microfiber cloth, and cable ties.', 119.00, 22, FALSE, 'https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80', JSON_ARRAY('https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80') FROM categories WHERE slug = 'parts-accessories'
ON DUPLICATE KEY UPDATE name = VALUES(name), category_id = VALUES(category_id), description = VALUES(description), price = VALUES(price), stock = VALUES(stock), featured = VALUES(featured), image_url = VALUES(image_url), gallery_json = VALUES(gallery_json);
