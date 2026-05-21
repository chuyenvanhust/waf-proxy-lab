#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/03_setup_dvwa.sh — Bước 3: Khởi tạo DVWA database
# Chỉ cần chạy 1 lần sau khi start lab lần đầu
# ─────────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 3: Setup DVWA     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "[1/2] Gọi DVWA setup.php để tạo database..."
# Gọi trực tiếp vào backend (không qua WAF) để tránh false positive
RESULT=$(docker exec backend \
  curl -s -o /dev/null -w "%{http_code}" \
  -X POST \
  --data "create_db=Create+%2F+Reset+Database" \
  http://localhost/dvwa/setup.php \
  2>/dev/null || echo "000")

if [ "$RESULT" = "200" ] || [ "$RESULT" = "302" ]; then
  echo "  ✓ Database DVWA đã được tạo (HTTP $RESULT)"
else
  echo "  ⚠ HTTP $RESULT — thử thủ công:"
  echo "    docker exec -it backend curl -X POST http://localhost/dvwa/setup.php \\"
  echo "      --data 'create_db=Create+%2F+Reset+Database'"
fi

echo ""
echo "[2/2] Set security level = low..."
docker exec backend \
  curl -s -o /dev/null \
  -X POST \
  --cookie "security=low; PHPSESSID=lab" \
  --data "security=low&seclev_submit=Submit" \
  http://localhost/dvwa/security.php \
  && echo "  ✓ Security level = low" \
  || echo "  ⚠ Set security level thất bại — set thủ công trong UI"

echo ""
echo "✅ DVWA đã sẵn sàng!"
echo ""
echo "   Truy cập DVWA: http://localhost/dvwa"
echo "   Login: admin / password"
echo "   Security level: low (cho lab)"
echo ""
echo "   Chạy tiếp: bash run/04_test_waf_off.sh"
