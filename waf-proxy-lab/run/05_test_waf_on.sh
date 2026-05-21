#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/05_test_waf_on.sh — Bước 5: Test khi WAF ở Blocking mode
# Mục đích: Xem WAF block các tấn công, đo tỷ lệ phát hiện
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 5: Test WAF ON        ║"
echo "║  (ModSecurity = On, blocking mode)          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Bật WAF blocking mode ─────────────────────────────────
echo "[1/5] Bật ModSecurity blocking mode..."
docker exec waf-server \
  sed -i 's/^SecRuleEngine DetectionOnly/SecRuleEngine On/' \
  /etc/modsecurity/modsecurity.conf

docker exec waf-server nginx -s reload
sleep 2
echo "  ✓ WAF = On (blocking mode)"

echo ""
echo "[2/5] Xác nhận WAF đang block..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost/vulnerabilities/sqli/?id=1'+OR+'1'='1&Submit=Submit" \
  --cookie "security=low; PHPSESSID=lab")
if [ "$CODE" = "403" ]; then
  echo "  ✓ SQLi bị block: HTTP 403"
else
  echo "  ✗ SQLi không bị block (HTTP $CODE) — kiểm tra cấu hình WAF"
  exit 1
fi

echo ""
echo "[3/5] Chạy tất cả test scripts (WAF ON)..."
mkdir -p "$ROOT/logs/results_on"

docker exec attacker python3 /opt/attack/scripts/test_sqli.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/sqli.txt \
  --output /opt/logs/results_on/sqli.json \
  --verbose

docker exec attacker python3 /opt/attack/scripts/test_xss.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/xss.txt \
  --output /opt/logs/results_on/xss.json \
  --verbose

docker exec attacker python3 /opt/attack/scripts/test_traversal.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/path-traversal.txt \
  --output /opt/logs/results_on/traversal.json \
  --verbose

echo ""
echo "[4/5] Đo false positive (request hợp lệ)..."
docker exec attacker python3 /opt/attack/scripts/test_normal.py \
  --target http://waf-server \
  --output /opt/logs/results_on/false_positive.json

echo ""
echo "[5/5] Kết quả lưu tại: logs/results_on/"
echo ""
echo "✅ Test WAF ON hoàn thành!"
echo "   Chạy tiếp: bash run/06_analyze_logs.sh"
