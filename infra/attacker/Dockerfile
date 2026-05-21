FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

# ── Cài tools tấn công ───────────────────────────────
RUN apt-get update && apt-get install -y \
    sqlmap \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# ── Cài XSStrike ─────────────────────────────────────
RUN git clone --depth 1 \
    https://github.com/s0md3v/XSStrike \
    /opt/XSStrike \
    && pip3 install -r /opt/XSStrike/requirements.txt --break-system-packages

# ── Cài thư viện Python cho test scripts ─────────────
RUN pip3 install requests colorama tabulate --break-system-packages

WORKDIR /opt/attack
CMD ["bash"]
