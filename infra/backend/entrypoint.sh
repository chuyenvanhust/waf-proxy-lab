#!/bin/bash
set -e

echo "[backend] Khởi động MySQL..."
service mariadb start
sleep 4

echo "[backend] Tạo database DVWA..."
mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS dvwa;
CREATE USER IF NOT EXISTS 'dvwa'@'localhost' IDENTIFIED BY 'p@ssw0rd';
GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "[backend] Khởi tạo schema DVWA..."
mysql -u dvwa -p'p@ssw0rd' dvwa < /var/www/html/dvwa/database/dvwa.mdf 2>/dev/null || true

echo "[backend] Khởi động Apache..."
apache2-foreground
