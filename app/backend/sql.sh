mysql -u root --execute="ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'bonjour';
FLUSH PRIVILEGES;
"
mysql -u root --password='bonjour' --execute='CREATE DATABASE IF NOT EXISTS BDD_VMs;'

mysql -u root --password='bonjour' --database=BDD_VMs --execute="
CREATE TABLE IF NOT EXISTS edge (
    nom VARCHAR(255) PRIMARY KEY,
    cpu INT NOT NULL,
    ram INT NOT NULL,
    statut VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS iot (
    nom VARCHAR(255) PRIMARY KEY,
    cpu INT NOT NULL,
    ram INT NOT NULL,
    statut VARCHAR(255),
    cluster VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS applications (
    nom VARCHAR(255) PRIMARY KEY,
    manifest TEXT
);

CREATE TABLE IF NOT EXISTS associations (
    cluster VARCHAR(255),
    application VARCHAR(255),
    manifest TEXT,
    PRIMARY KEY (cluster,application),
    FOREIGN KEY (cluster) REFERENCES applications(nom)
);
"