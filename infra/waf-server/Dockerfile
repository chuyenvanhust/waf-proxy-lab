FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ── Cài dependencies ──────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    libpcre3 \
    libpcre3-dev \
    libpcre2-dev \
    libssl-dev \
    libtool \
    autoconf \
    automake \
    pkg-config \
    libcurl4-openssl-dev \
    libgeoip-dev \
    libyajl-dev \
    libfuzzy-dev \
    libxml2 \
    libxml2-dev \
    libpcre++-dev \
    liblmdb-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# ── Build ModSecurity v3 từ source ───────────────────
RUN git clone --recursive \
    https://github.com/owasp-modsecurity/ModSecurity \
    /opt/ModSecurity \
    && cd /opt/ModSecurity \
    && ./build.sh \
    && ./configure \
    && make -j$(nproc) \
    && make install

# ── Build ModSecurity-nginx connector ────────────────
RUN git clone --depth 1 \
    https://github.com/owasp-modsecurity/ModSecurity-nginx \
    /opt/ModSecurity-nginx

RUN NGINX_VERSION=$(dpkg -s nginx | grep Version | awk '{print $2}' | cut -d'-' -f1) \
    && echo "Building nginx module for version: ${NGINX_VERSION}" \
    && wget -q http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -xzf nginx-${NGINX_VERSION}.tar.gz \
    && cd nginx-${NGINX_VERSION} \
    && ./configure \
        --with-compat \
        --without-http_gzip_module \
        --add-dynamic-module=/opt/ModSecurity-nginx \
    && make modules \
    && cp objs/ngx_http_modsecurity_module.so \
       /usr/lib/nginx/modules/ngx_http_modsecurity_module.so \
    && rm -rf /nginx-${NGINX_VERSION}*

# ── Clone OWASP CRS ──────────────────────────────────
RUN git clone --depth 1 \
    https://github.com/coreruleset/coreruleset \
    /etc/nginx/modsecurity-crs \
    && cp /etc/nginx/modsecurity-crs/crs-setup.conf.example \
          /etc/nginx/modsecurity-crs/crs-setup.conf.example.bak

# ── Copy config ──────────────────────────────────────
COPY waf/nginx/nginx.conf              /etc/nginx/nginx.conf
COPY waf/nginx/waf-site.conf           /etc/nginx/conf.d/default.conf
COPY waf/nginx/proxy-params.conf       /etc/nginx/proxy-params.conf
COPY waf/modsecurity/modsecurity.conf  /etc/modsecurity/modsecurity.conf
COPY waf/modsecurity/crs-setup.conf    /etc/nginx/modsecurity-crs/crs-setup.conf
COPY waf/modsecurity/custom-rules.conf /etc/nginx/modsecurity-crs/rules/custom-rules.conf

# ── Tạo thư mục log ──────────────────────────────────
RUN mkdir -p /var/log/modsec /tmp/modsecurity \
    && touch /var/log/modsec/audit.log \
    && touch /var/log/modsec/debug.log

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
