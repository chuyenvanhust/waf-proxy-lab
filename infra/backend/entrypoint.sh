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

echo "[backend] Database sẵn sàng, DVWA sẽ tự setup qua web..."

echo "[backend] Khởi động Apache..."
apache2-foreground
