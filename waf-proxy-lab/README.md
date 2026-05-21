# waf-proxy-lab

> **Môn:** An toàn thông tin | **Chủ đề:** Proxy — Cấu trúc, hoạt động và ứng dụng trong WAF

---

## Cấu trúc dự án

```
waf-proxy-lab/
│
├── run/                        ← CHẠY TỪ ĐÂY
│   ├── run_all.sh              ← Chạy toàn bộ pipeline 1 lệnh
│   ├── 01_build.sh             ← Build Docker images
│   ├── 02_start.sh             ← Khởi động containers
│   ├── 03_setup_dvwa.sh        ← Khởi tạo DVWA database
│   ├── 04_test_waf_off.sh      ← Test baseline (WAF tắt)
│   ├── 05_test_waf_on.sh       ← Test blocking (WAF bật)
│   ├── 06_analyze_logs.sh      ← Phân tích log
│   ├── 07_compare.sh           ← So sánh WAF ON vs OFF
│   └── 08_stop.sh              ← Dừng lab
│
├── infra/                      ← Docker & mạng [A+B]
│   ├── docker-compose.yml
│   ├── waf-server/Dockerfile   [A]
│   ├── backend/Dockerfile      [B]
│   └── attacker/Dockerfile     [B]
│
├── waf/                        ← Cấu hình WAF [A]
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── waf-site.conf
│   │   └── proxy-params.conf
│   └── modsecurity/
│       ├── modsecurity.conf
│       ├── crs-setup.conf
│       └── custom-rules.conf
│
├── attack/                     ← Payload & scripts [B]
│   ├── payloads/
│   │   ├── sqli.txt
│   │   ├── xss.txt
│   │   └── path-traversal.txt
│   └── scripts/
│       ├── test_sqli.py
│       ├── test_xss.py
│       ├── test_traversal.py
│       ├── test_normal.py
│       └── run_all_tests.py
│
├── logs/                       ← Log & phân tích [A]
│   ├── parse_logs.py
│   └── report.py
│
└── .devcontainer/              ← GitHub Codespaces config
    └── devcontainer.json
```

---

## Chạy nhanh (1 lệnh)

```bash
# Clone repo
git clone https://github.com/<org>/waf-proxy-lab.git
cd waf-proxy-lab

# Cấp quyền
chmod +x run/*.sh

# Chạy toàn bộ pipeline
bash run/run_all.sh
```

---

## Chạy từng bước

```bash
bash run/01_build.sh        # Build 3 Docker images
bash run/02_start.sh        # Khởi động waf-server, backend, attacker
bash run/03_setup_dvwa.sh   # Khởi tạo database DVWA (1 lần)
bash run/04_test_waf_off.sh # Test khi WAF ở DetectionOnly
bash run/05_test_waf_on.sh  # Test khi WAF ở Blocking mode
bash run/06_analyze_logs.sh # Phân tích modsec_audit.log
bash run/07_compare.sh      # So sánh kết quả
bash run/08_stop.sh         # Dừng lab
```

---

## Kiến trúc

```
[Attacker container]
      │  HTTP + payload
      ▼
[WAF Server :80]        ← Nginx + ModSecurity + OWASP CRS
      │
  ┌───┴───┐
  │ BLOCK │ → HTTP 403 + ghi audit.log
  │ PASS  │ → forward đến backend
  └───────┘
      │
[Backend container]     ← DVWA (PHP + MySQL)
```

---

## Phân công

| Phần | Người A | Người B |
|------|---------|---------|
| `waf/` | ✓ | |
| `logs/` | ✓ | |
| `infra/waf-server/` | ✓ | |
| `attack/` | | ✓ |
| `infra/backend/` + `attacker/` | | ✓ |
| `run/` · `infra/docker-compose.yml` | ✓ | ✓ |
