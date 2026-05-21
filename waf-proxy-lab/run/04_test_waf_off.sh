#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/04_test_waf_off.sh — Bước 4: Test khi WAF ở DetectionOnly
# Mục đích: Xem tấn công đi qua khi không bị block
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 4: Test WAF OFF       ║"
echo "║  (ModSecurity = DetectionOnly, chỉ log)     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Chuyển WAF sang DetectionOnly ────────────────────────
echo "[1/4] Chuyển ModSecurity sang DetectionOnly..."
docker exec waf-server \
  sed -i 's/^SecRuleEngine On/SecRuleEngine DetectionOnly/' \
  /etc/modsecurity/modsecurity.conf

docker exec waf-server nginx -s reload
sleep 2
echo "  ✓ WAF = DetectionOnly (log nhưng không block)"

echo ""
echo "[2/4] Kiểm tra nhanh SQLi qua..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost/vulnerabilities/sqli/?id=1'+OR+'1'='1&Submit=Submit" \
  --cookie "security=low; PHPSESSID=lab")
echo "  SQLi payload → HTTP $CODE (mong đợi: 200 = đi qua được)"

echo ""
echo "[3/4] Chạy toàn bộ test scripts (WAF OFF)..."
mkdir -p "$ROOT/logs/results_off"

docker exec attacker python3 /opt/attack/scripts/test_sqli.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/sqli.txt \
  --output /opt/logs/results_off/sqli.json \
  --verbose

docker exec attacker python3 /opt/attack/scripts/test_xss.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/xss.txt \
  --output /opt/logs/results_off/xss.json \
  --verbose

docker exec attacker python3 /opt/attack/scripts/test_traversal.py \
  --target http://waf-server \
  --payload-file /opt/attack/payloads/path-traversal.txt \
  --output /opt/logs/results_off/traversal.json \
  --verbose

echo ""
echo "[4/4] Kết quả lưu tại: logs/results_off/"
echo ""
echo "✅ Test WAF OFF hoàn thành!"
echo "   → Ghi lại kết quả để so sánh với WAF ON"
echo "   Chạy tiếp: bash run/05_test_waf_on.sh"
