CREATE TABLE toxicite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(255) NOT NULL
);

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(255) NOT NULL
);

CREATE TABLE additifs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    toxicite_id INT,
    description TEXT,
    description_avancee TEXT,
    remarques TEXT,
    FOREIGN KEY (toxicite_id) REFERENCES toxicite(id)
);

CREATE TABLE additifs_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_additif VARCHAR(50) NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (code_additif) REFERENCES additifs(code),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE additifs_noms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_additif VARCHAR(50) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    FOREIGN KEY (code_additif) REFERENCES additifs(code)
);

CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);