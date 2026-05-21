FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ── Cài Nginx và ModSecurity ──────────────────────────
RUN apt-get update && apt-get install -y \
    nginx \
    libmodsecurity3 \
    libmodsecurity-dev \
    libnginx-mod-http-modsecurity \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# ── Clone OWASP Core Rule Set ─────────────────────────
RUN git clone --depth 1 \
    https://github.com/coreruleset/coreruleset \
    /etc/nginx/modsecurity-crs

# ── Copy cấu hình từ repo ─────────────────────────────
COPY waf/nginx/nginx.conf              /etc/nginx/nginx.conf
COPY waf/nginx/waf-site.conf           /etc/nginx/conf.d/default.conf
COPY waf/modsecurity/modsecurity.conf  /etc/modsecurity/modsecurity.conf
COPY waf/modsecurity/crs-setup.conf    /etc/nginx/modsecurity-crs/crs-setup.conf
COPY waf/modsecurity/custom-rules.conf /etc/nginx/modsecurity-crs/rules/custom-rules.conf

# ── Tạo thư mục log ──────────────────────────────────
RUN mkdir -p /var/log/modsec \
    && touch /var/log/modsec/audit.log \
    && ln -sf /var/log/modsec/audit.log /var/log/modsec_audit.log

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
