#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/02_start.sh — Bước 2: Khởi động toàn bộ lab
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 2: Start Lab      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Tạo thư mục logs nếu chưa có
mkdir -p logs
touch logs/audit.log

echo "[1/3] Khởi động containers..."
docker compose \
  --file infra/docker-compose.yml \
  --project-name waf-lab \
  up -d

echo ""
echo "[2/3] Chờ services sẵn sàng..."
sleep 8

# Kiểm tra health từng container
check_container() {
  local name=$1
  if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
    echo "  ✓ $name đang chạy"
  else
    echo "  ✗ $name KHÔNG chạy — xem log: docker logs $name"
    exit 1
  fi
}

check_container "waf-server"
check_container "backend"
check_container "attacker"

echo ""
echo "[3/3] Kiểm tra WAF nhận request..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  --max-time 10 http://localhost/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
  echo "  ✓ WAF phản hồi: HTTP $HTTP_CODE"
else
  echo "  ⚠ WAF trả: HTTP $HTTP_CODE (có thể backend chưa sẵn sàng, thử lại sau 10s)"
fi

echo ""
echo "✅ Lab đang chạy!"
echo ""
echo "   WAF URL  : http://localhost"
echo "   DVWA     : http://localhost/dvwa (qua WAF)"
echo "   Log file : $ROOT/logs/audit.log"
echo ""
echo "   Vào attacker: docker exec -it attacker bash"
echo "   Chạy tiếp  : bash run/03_setup_dvwa.sh"
