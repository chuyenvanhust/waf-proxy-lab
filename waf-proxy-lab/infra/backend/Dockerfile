FROM php:8.1-apache

ENV DEBIAN_FRONTEND=noninteractive

# ── Cài MySQL và extension PHP ───────────────────────
RUN apt-get update && apt-get install -y \
    default-mysql-server \
    default-mysql-client \
    && docker-php-ext-install mysqli pdo pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

# ── Clone DVWA ────────────────────────────────────────
RUN git clone --depth 1 \
    https://github.com/digininja/DVWA.git \
    /var/www/html/dvwa

# ── Cấu hình DVWA ────────────────────────────────────
COPY infra/backend/dvwa-config.php /var/www/html/dvwa/config/config.inc.php

# ── Quyền truy cập ───────────────────────────────────
RUN chown -R www-data:www-data /var/www/html/dvwa \
    && chmod -R 755 /var/www/html/dvwa

# ── Script khởi động ──────────────────────────────────
COPY infra/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
CMD ["/entrypoint.sh"]
