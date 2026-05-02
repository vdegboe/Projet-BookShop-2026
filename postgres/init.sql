-- Suppression des tables dans l'ordre inverse des dépendances
DROP TABLE IF EXISTS ventes;
DROP TABLE IF EXISTS factures;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS category;

-- TABLE category
CREATE TABLE category (
    id         SERIAL PRIMARY KEY,
    intitule   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE books
CREATE TABLE books (
    id          SERIAL PRIMARY KEY,
    category_id INT REFERENCES category(id),
    code        VARCHAR(50)  UNIQUE NOT NULL,
    intitule    VARCHAR(255) NOT NULL,
    isbn_10     VARCHAR(10),
    isbn_13     VARCHAR(13),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE customers
CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(50)  UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE factures
CREATE TABLE factures (
    id           SERIAL PRIMARY KEY,
    code         VARCHAR(50)    UNIQUE NOT NULL,
    date_edit    VARCHAR(8)     NOT NULL, -- Format YYYYMMDD
    customers_id INT REFERENCES customers(id),
    qte_totale   INT            DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_paid   DECIMAL(10, 2) DEFAULT 0.00,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE ventes
CREATE TABLE ventes (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(50)    UNIQUE NOT NULL,
    date_edit   VARCHAR(8)     NOT NULL, -- Format YYYYMMDD
    factures_id INT REFERENCES factures(id),
    books_id    INT REFERENCES books(id),
    pu          DECIMAL(10, 2) NOT NULL,
    qte         INT            NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- DONNÉES DE TEST — Librairie
-- ============================================================

-- CATÉGORIES (7 genres)
INSERT INTO category (intitule) VALUES
    ('Roman Africain'),
    ('Littérature Jeunesse'),
    ('Histoire & Politique'),
    ('Développement Personnel'),
    ('Philosophie & Essai'),
    ('Policier & Thriller'),
    ('Poésie & Théâtre');

-- LIVRES 
INSERT INTO books (category_id, code, intitule, isbn_10, isbn_13) VALUES
    -- Romans africains
    (1, 'BK001', 'Doguicimi — Paul Hazoumé (Bénin)',             '2708702688', '9782708702684'),
    (1, 'BK002', 'Un Piège sans fin — Olympe Bhêly-Quenum (Bénin)', '2708700030', '9782708700031'),
    (1, 'BK003', 'Notre Prison est un Royaume — F. Couao-Zotti (Bénin)', '2738113567', '9782738113566'),
    (1, 'BK004', 'Le Monde s''effondre — Chinua Achebe (Nigéria)',       '2070368262', '9782070368266'),
    (1, 'BK005', 'Americanah — Chimamanda Ngozi Adichie (Nigéria)',      '2072481953', '9782072481956'),
    (1, 'BK006', 'L''Hibiscus pourpre — Chimamanda N. Adichie (Nigéria)','2072481961', '9782072481963'),
    (1, 'BK007', 'La Route de la faim — Ben Okri (Nigéria)',             '2253150681', '9782253150688'),
    (1, 'BK008', 'Les Soleils des indépendances — A. Kourouma (CI)',     '2020059290', '9782020059299'),
    (1, 'BK009', 'Allah n''est pas obligé — Ahmadou Kourouma (CI)',      '2020528991', '9782020528993'),
    (1, 'BK010', 'Climbié — Bernard Dadié (CI)',                         '2708700480', '9782708700482'),
    (1, 'BK011', 'Un Nègre à Paris — Bernard Dadié (CI)',                '2708700197', '9782708700192'),
    (1, 'BK012', 'Reine Pokou — Véronique Tadjo (CI)',                   '2844501524', '9782844501523'),

    -- Histoire & Politique
    (3, 'BK013', 'Histoire du Dahomey — Édouard Dunglas',               '0000000001', '9780000000001'),
    (3, 'BK014', 'L''Afrique noire est mal partie — R. Dumont',          '2020028050', '9782020028059'),

    -- Développement Personnel
    (4, 'BK015', 'Le Leadership Africain — J.-C. Gnamien',              '0000000002', '9780000000002'),
    (4, 'BK016', 'L''Art de réussir en Afrique — Strive Masiyiwa',       '0000000003', '9780000000003'),

    -- Philosophie & Essai
    (5, 'BK017', 'L''Aventure ambiguë — Cheikh Hamidou Kane (Sénégal)', '2708700685', '9782708700680'),
    (5, 'BK018', 'La Carte d''identité — Jean-Marie Adiaffi (CI)',       '2708701118', '9782708701114'),

    -- Policier & Thriller
    (6, 'BK019', 'Soro — Florent Couao-Zotti (Bénin)',                  '2080681338', '9782080681331'),

    -- Poésie & Théâtre
    (7, 'BK020', 'Afrique debout ! — Bernard Dadié (CI)',               '2708700014', '9782708700018');

-- CLIENTS 
INSERT INTO customers (code, first_name, last_name) VALUES
    -- Béninois
    ('CLI001', 'Viwossin',   'DEGBOE'),
    ('CLI002', 'Romuald',    'AHOYO'),
    ('CLI003', 'Félicité',   'ZINSOU'),
    ('CLI004', 'Médard',     'KPOSSINOU'),
    ('CLI005', 'Chidinma',   'OKAFOR'),
    ('CLI006', 'Babatunde',  'ADEYEMI'),
    ('CLI007', 'Ifeanyi',    'NWOSU'),
    ('CLI008', 'Tunde',      'ABIODUN'),
    ('CLI009', 'Adjoua',     'KOUASSI'),
    ('CLI010', 'Aminata',    'DIOMANDE'),
    ('CLI011', 'Seydou',     'BAMBA'),
    ('CLI012', 'Koffi',      'YAO');

-- ============================================================
-- FACTURES 
-- ============================================================
INSERT INTO factures (code, date_edit, customers_id, qte_totale, total_amount, total_paid) VALUES
    -- 2023 — T1
    ('FAC001', '20230112',  1, 2,  54.00,  54.00),
    ('FAC002', '20230128',  3, 1,  22.00,  22.00),
    ('FAC003', '20230215',  2, 3,  72.00,  72.00),
    ('FAC004', '20230301',  5, 2,  38.00,  38.00),
    ('FAC005', '20230320',  4, 1,  29.00,  29.00),
    -- 2023 — T2
    ('FAC006', '20230405',  6, 2,  48.00,  48.00),
    ('FAC007', '20230418',  1, 3,  81.00,  81.00),
    ('FAC008', '20230510',  7, 1,  25.00,  25.00),
    ('FAC009', '20230527',  2, 2,  44.00,  44.00),
    ('FAC010', '20230614',  8, 4, 104.00, 104.00),
    -- 2023 — T3
    ('FAC011', '20230703',  9, 1,  19.00,  19.00),
    ('FAC012', '20230722',  3, 2,  56.00,  56.00),
    ('FAC013', '20230808', 10, 3,  75.00,  75.00),
    ('FAC014', '20230819',  5, 1,  32.00,  32.00),
    ('FAC015', '20230904', 11, 2,  60.00,  60.00),
    -- 2023 — T4
    ('FAC016', '20231005', 12, 1,  28.00,  28.00),
    ('FAC017', '20231020',  4, 3,  90.00,  90.00),
    ('FAC018', '20231105',  6, 2,  58.00,  58.00),
    ('FAC019', '20231118',  1, 4, 108.00, 100.00),
    ('FAC020', '20231210',  7, 2,  46.00,  46.00),
    -- 2024 — T1
    ('FAC021', '20240108',  8, 1,  24.00,  24.00),
    ('FAC022', '20240122',  2, 3,  84.00,  84.00),
    ('FAC023', '20240205',  9, 2,  52.00,  52.00),
    ('FAC024', '20240214', 10, 1,  31.00,  31.00),
    ('FAC025', '20240307', 11, 2,  66.00,  66.00),
    -- 2024 — T2
    ('FAC026', '20240402', 12, 3,  87.00,  87.00),
    ('FAC027', '20240416',  3, 1,  22.00,  22.00),
    ('FAC028', '20240503',  5, 4, 112.00, 112.00),
    ('FAC029', '20240520',  6, 2,  50.00,  50.00),
    ('FAC030', '20240611',  4, 1,  27.00,  27.00),
    -- 2024 — T3
    ('FAC031', '20240704',  7, 3,  93.00,  93.00),
    ('FAC032', '20240718',  8, 2,  62.00,  62.00),
    ('FAC033', '20240801',  1, 1,  35.00,  35.00),
    ('FAC034', '20240822',  9, 2,  70.00,  60.00),
    ('FAC035', '20240909',  2, 3,  81.00,  81.00),
    -- 2024 — T4
    ('FAC036', '20241003', 10, 2,  54.00,  54.00),
    ('FAC037', '20241017', 11, 1,  29.00,  29.00),
    ('FAC038', '20241105', 12, 4, 116.00, 116.00),
    ('FAC039', '20241119',  3, 2,  48.00,  48.00),
    ('FAC040', '20241208',  5, 3,  75.00,  75.00);

-- ============================================================
-- VENTES (60 lignes de vente liées aux factures)
-- ============================================================
INSERT INTO ventes (code, date_edit, factures_id, books_id, pu, qte) VALUES
    -- FAC001 (2 livres)
    ('VNT001', '20230112',  1,  1, 27.00, 1),
    ('VNT002', '20230112',  1, 15, 27.00, 1),
    -- FAC002 (1 livre)
    ('VNT003', '20230128',  2, 17, 22.00, 1),
    -- FAC003 (3 livres)
    ('VNT004', '20230215',  3,  4, 24.00, 1),
    ('VNT005', '20230215',  3,  8, 24.00, 1),
    ('VNT006', '20230215',  3, 18, 24.00, 1),
    -- FAC004 (2 livres)
    ('VNT007', '20230301',  4,  5, 19.00, 2),
    -- FAC005 (1 livre)
    ('VNT008', '20230320',  5, 19, 29.00, 1),
    -- FAC006 (2 livres)
    ('VNT009', '20230405',  6, 16, 24.00, 2),
    -- FAC007 (3 livres)
    ('VNT010', '20230418',  7,  2, 27.00, 1),
    ('VNT011', '20230418',  7,  9, 27.00, 1),
    ('VNT012', '20230418',  7, 13, 27.00, 1),
    -- FAC008 (1 livre)
    ('VNT013', '20230510',  8, 20, 25.00, 1),
    -- FAC009 (2 livres)
    ('VNT014', '20230527',  9, 10, 22.00, 2),
    -- FAC010 (4 livres)
    ('VNT015', '20230614', 10,  3, 26.00, 1),
    ('VNT016', '20230614', 10,  6, 26.00, 1),
    ('VNT017', '20230614', 10, 11, 26.00, 1),
    ('VNT018', '20230614', 10, 14, 26.00, 1),
    -- FAC011 (1 livre)
    ('VNT019', '20230703', 11, 17, 19.00, 1),
    -- FAC012 (2 livres)
    ('VNT020', '20230722', 12, 19, 28.00, 2),
    -- FAC013 (3 livres)
    ('VNT021', '20230808', 13,  7, 25.00, 1),
    ('VNT022', '20230808', 13, 12, 25.00, 1),
    ('VNT023', '20230808', 13,  1, 25.00, 1),
    -- FAC014 (1 livre)
    ('VNT024', '20230819', 14,  5, 32.00, 1),
    -- FAC015 (2 livres)
    ('VNT025', '20230904', 15, 16, 30.00, 2),
    -- FAC016 (1 livre)
    ('VNT026', '20231005', 16, 18, 28.00, 1),
    -- FAC017 (3 livres)
    ('VNT027', '20231020', 17,  4, 30.00, 1),
    ('VNT028', '20231020', 17,  8, 30.00, 1),
    ('VNT029', '20231020', 17, 15, 30.00, 1),
    -- FAC018 (2 livres)
    ('VNT030', '20231105', 18, 19, 29.00, 2),
    -- FAC019 (4 livres)
    ('VNT031', '20231118', 19,  9, 27.00, 1),
    ('VNT032', '20231118', 19, 13, 27.00, 1),
    ('VNT033', '20231118', 19,  3, 27.00, 1),
    ('VNT034', '20231118', 19, 17, 27.00, 1),
    -- FAC020 (2 livres)
    ('VNT035', '20231210', 20, 11, 23.00, 2),
    -- FAC021 (1 livre)
    ('VNT036', '20240108', 21,  6, 24.00, 1),
    -- FAC022 (3 livres)
    ('VNT037', '20240122', 22, 14, 28.00, 1),
    ('VNT038', '20240122', 22,  2, 28.00, 1),
    ('VNT039', '20240122', 22,  7, 28.00, 1),
    -- FAC023 (2 livres)
    ('VNT040', '20240205', 23, 15, 26.00, 2),
    -- FAC024 (1 livre)
    ('VNT041', '20240214', 24, 20, 31.00, 1),
    -- FAC025 (2 livres)
    ('VNT042', '20240307', 25, 16, 33.00, 2),
    -- FAC026 (3 livres)
    ('VNT043', '20240402', 26, 10, 29.00, 1),
    ('VNT044', '20240402', 26, 12, 29.00, 1),
    ('VNT045', '20240402', 26,  4, 29.00, 1),
    -- FAC027 (1 livre)
    ('VNT046', '20240416', 27, 18, 22.00, 1),
    -- FAC028 (4 livres)
    ('VNT047', '20240503', 28,  5, 28.00, 1),
    ('VNT048', '20240503', 28, 13, 28.00, 1),
    ('VNT049', '20240503', 28,  9, 28.00, 1),
    ('VNT050', '20240503', 28,  1, 28.00, 1),
    -- FAC029 (2 livres)
    ('VNT051', '20240520', 29, 11, 25.00, 2),
    -- FAC030 (1 livre)
    ('VNT052', '20240611', 30,  3, 27.00, 1),
    -- FAC031 (3 livres)
    ('VNT053', '20240704', 31,  6, 31.00, 1),
    ('VNT054', '20240704', 31, 19, 31.00, 1),
    ('VNT055', '20240704', 31,  2, 31.00, 1),
    -- FAC032 (2 livres)
    ('VNT056', '20240718', 32,  8, 31.00, 2),
    -- FAC033 (1 livre)
    ('VNT057', '20240801', 33, 17, 35.00, 1),
    -- FAC034 (2 livres)
    ('VNT058', '20240822', 34, 14, 35.00, 2),
    -- FAC035 (3 livres)
    ('VNT059', '20240909', 35, 15, 27.00, 1),
    ('VNT060', '20240909', 35,  5, 27.00, 1);
