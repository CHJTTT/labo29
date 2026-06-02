-- =====================================================
-- TECHSTORE — SETUP COMPLETO DE BASE DE DATOS
-- Ejecuta esto en tu consola de Neon PostgreSQL
-- =====================================================

-- ── TABLA USUARIOS ──────────────────────────────────
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id_usr    SERIAL PRIMARY KEY,
    nombre    VARCHAR(100) NOT NULL,
    correo    VARCHAR(150) NOT NULL UNIQUE,
    pin       CHAR(4) NOT NULL,
    rol       VARCHAR(20) NOT NULL DEFAULT 'cliente',
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Admin por defecto (PIN: 1234)
INSERT INTO usuarios (nombre, correo, pin, rol) VALUES
('Administrador', 'admin@techstore.com', '1234', 'admin');

-- ── TABLA PRODUCTOS ──────────────────────────────────
DROP TABLE IF EXISTS productos;

CREATE TABLE productos (
    id_pro     SERIAL PRIMARY KEY,
    nom_pro    VARCHAR(100) NOT NULL,
    pre_pro    DECIMAL(10,2) NOT NULL,
    stk_pro    INT NOT NULL,
    ventas     INT DEFAULT 0,
    categoria  VARCHAR(50) DEFAULT 'General',
    img_url    TEXT,
    oferta     BOOLEAN DEFAULT FALSE,
    pre_oferta DECIMAL(10,2)
);

INSERT INTO productos (nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta) VALUES
-- PERIFÉRICOS
('Mouse Óptico Pro', 45.50, 150, 320, 'Periféricos', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80', false, null),
('Teclado Razer Huntsman', 320.00, 8, 95, 'Periféricos', 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=600&q=80', true, 259.00),
('Teclado Mecánico Keychron K2', 180.00, 35, 140, 'Periféricos', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80', false, null),
('Mouse Logitech MX Master 3', 120.00, 45, 280, 'Periféricos', 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&q=80', true, 89.00),
('Mousepad XL RGB', 55.00, 90, 210, 'Periféricos', 'https://images.unsplash.com/photo-1616763355548-1b606f439f86?w=600&q=80', false, null),
('Teclado Inalámbrico Logitech K380', 95.00, 60, 175, 'Periféricos', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80', true, 69.00),
-- MONITORES
('Monitor Asus 4K 27"', 850.00, 12, 61, 'Monitores', 'https://images.unsplash.com/photo-1527443224154-c4a573d5a27e?w=600&q=80', false, null),
('Monitor LG UltraWide 34"', 1100.00, 7, 43, 'Monitores', 'https://images.unsplash.com/photo-1593640408182-31c228ef94f2?w=600&q=80', true, 849.00),
('Monitor Samsung 24" FHD', 380.00, 25, 98, 'Monitores', 'https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&q=80', false, null),
('Monitor Portátil Asus ZenScreen', 420.00, 18, 67, 'Monitores', 'https://images.unsplash.com/photo-1527443224154-c4a573d5a27e?w=600&q=80', true, 329.00),
-- AUDIO
('Auriculares Sony WH-1000XM5', 450.00, 20, 210, 'Audio', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80', false, null),
('Micrófono Blue Yeti X', 220.00, 18, 175, 'Audio', 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&q=80', true, 169.00),
('Auriculares HyperX Cloud III', 180.00, 30, 195, 'Audio', 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&q=80', false, null),
('Bocina JBL Charge 5', 220.00, 40, 230, 'Audio', 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80', true, 179.00),
('Auriculares Apple AirPods Pro 2', 380.00, 25, 310, 'Audio', 'https://images.unsplash.com/photo-1588156979435-379b9d802b0a?w=600&q=80', false, null),
('Bocina Sonos Era 100', 350.00, 15, 88, 'Audio', 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80', true, 279.00),
-- LAPTOPS
('Laptop Lenovo ThinkPad X1', 3200.00, 5, 38, 'Laptops', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80', false, null),
('MacBook Air M3 13"', 2800.00, 8, 72, 'Laptops', 'https://images.unsplash.com/photo-1611186871525-dd2c62c3900a?w=600&q=80', true, 2399.00),
('Laptop Asus ROG Zephyrus', 3500.00, 4, 29, 'Laptops', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&q=80', false, null),
('Laptop Dell XPS 15', 2600.00, 6, 45, 'Laptops', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80', true, 2149.00),
('Chromebook HP 14"', 650.00, 20, 88, 'Laptops', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80', false, null),
-- ALMACENAMIENTO
('SSD Samsung 1TB NVMe', 180.00, 60, 430, 'Almacenamiento', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80', false, null),
('SSD Externo WD 2TB', 220.00, 45, 310, 'Almacenamiento', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80', true, 169.00),
('Pendrive Kingston 256GB', 45.00, 120, 520, 'Almacenamiento', 'https://images.unsplash.com/photo-1618517351616-38fb9c5210c6?w=600&q=80', false, null),
('Disco Duro Seagate 4TB', 280.00, 35, 190, 'Almacenamiento', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80', true, 219.00),
('NAS Synology DS223', 620.00, 10, 42, 'Almacenamiento', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80', false, null),
-- TABLETS
('iPad Pro M4 11"', 1200.00, 15, 88, 'Tablets', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80', true, 999.00),
('Samsung Galaxy Tab S9', 950.00, 12, 65, 'Tablets', 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=600&q=80', false, null),
('iPad Mini 7"', 720.00, 18, 95, 'Tablets', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80', true, 599.00),
('Wacom Intuos Pro M', 480.00, 14, 55, 'Tablets', 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=600&q=80', false, null),
-- GAMING
('Controlador Xbox Elite 2', 195.00, 30, 310, 'Gaming', 'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=600&q=80', false, null),
('DualSense PS5 Edge', 220.00, 25, 275, 'Gaming', 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=600&q=80', true, 179.00),
('Silla Gamer SecretLab Titan', 890.00, 7, 52, 'Gaming', 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80', false, null),
('Nintendo Switch OLED', 420.00, 20, 340, 'Gaming', 'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=80', true, 359.00),
('Steam Deck 512GB', 680.00, 10, 120, 'Gaming', 'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=600&q=80', false, null),
('Auriculares Astro A50 X', 380.00, 15, 98, 'Gaming', 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&q=80', true, 299.00),
-- ACCESORIOS
('Hub USB-C 12 en 1', 95.00, 80, 280, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80', false, null),
('Webcam Logitech 4K Pro', 280.00, 25, 145, 'Accesorios', 'https://images.unsplash.com/photo-1590156562745-5d0c3e6e27e1?w=600&q=80', true, 219.00),
('Cargador MagSafe 140W', 120.00, 50, 320, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80', false, null),
('Soporte Laptop Ergonómico', 75.00, 65, 410, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80', true, 55.00),
('Lámpara LED Monitor BenQ', 95.00, 40, 230, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80', false, null),
('Alfombrilla Qi Carga Inalámbrica', 65.00, 70, 290, 'Accesorios', 'https://images.unsplash.com/photo-1625242661561-bef7bf5e4bda?w=600&q=80', true, 45.00);