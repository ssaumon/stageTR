mysql -u root --execute='CREATE DATABASE IF NOT EXISTS BDD_VMs;'
mysql -u root --execute='USE BDD_VMs;'
mysql -u root --execute='USE BDD_VMs; CREATE TABLE IF NOT EXISTS edge (nom varchar(255) PRIMARY KEY ,cpu INT NOT NULL,ram INT NOT NULL, statut varchar(255));'
mysql -u root --execute='USE BDD_VMs; CREATE TABLE IF NOT EXISTS iot (nom varchar(255) PRIMARY KEY ,cpu INT NOT NULL,ram INT NOT NULL, statut varchar(255));'
mysql -u root --execute='USE BDD_VMs; CREATE TABLE IF NOT EXISTS applications (nom varchar(255) PRIMARY KEY , manifest TEXT(65535));'
mysql -u root --execute='ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'bonjour';
FLUSH PRIVILEGES;
'