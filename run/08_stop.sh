#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/08_stop.sh — Bước 8: Dừng và dọn dẹp lab
# ─────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 8: Stop Lab           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

echo "Dừng containers..."
docker compose \
  --file infra/docker-compose.yml \
  --project-name waf-lab \
  down

echo ""
echo "✅ Lab đã dừng."
echo ""
echo "   Logs vẫn còn tại: logs/"
echo "   Để xóa hoàn toàn: docker compose -f infra/docker-compose.yml down --volumes --rmi all"
