-- Ejecuta esto en tu consola de PostgreSQL dentro de techstore_db
DROP TABLE IF EXISTS productos;

CREATE TABLE productos (
    id_pro SERIAL PRIMARY KEY,
    nom_pro VARCHAR(100) NOT NULL,
    pre_pro DECIMAL(10,2) NOT NULL,
    stk_pro INT NOT NULL,
    ventas INT DEFAULT 0,
    categoria VARCHAR(50) DEFAULT 'General',
    img_url TEXT
);

INSERT INTO productos (nom_pro, pre_pro, stk_pro, ventas, categoria, img_url) VALUES
('Mouse Óptico Pro', 45.50, 150, 320, 'Periféricos', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80'),
('Teclado Razer Huntsman', 320.00, 8, 95, 'Periféricos', 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=600&q=80'),
('Monitor Asus 4K 27"', 850.00, 12, 61, 'Monitores', 'https://images.unsplash.com/photo-1527443224154-c4a573d5a27e?w=600&q=80'),
('Auriculares Sony WH-1000XM5', 450.00, 20, 210, 'Audio', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80'),
('Laptop Lenovo ThinkPad X1', 3200.00, 5, 38, 'Laptops', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80'),
('Webcam Logitech 4K Pro', 280.00, 25, 145, 'Periféricos', 'https://images.unsplash.com/photo-1590156562745-5d0c3e6e27e1?w=600&q=80'),
('SSD Samsung 1TB NVMe', 180.00, 60, 430, 'Almacenamiento', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80'),
('iPad Pro M4 11"', 1200.00, 15, 88, 'Tablets', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80'),
('Silla Gamer SecretLab', 890.00, 7, 52, 'Mobiliario', 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80'),
('Hub USB-C 12 en 1', 95.00, 80, 280, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80'),
('Micrófono Blue Yeti X', 220.00, 18, 175, 'Audio', 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&q=80'),
('Controlador Xbox Elite 2', 195.00, 30, 310, 'Gaming', 'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=600&q=80');