#!/bin/bash
# ═══════════════════════════════════════════════════════════
# run/run_all.sh — Chạy TOÀN BỘ lab từ đầu đến cuối
#
# Dùng: bash run/run_all.sh
#        bash run/run_all.sh --skip-build   (nếu đã build rồi)
# ═══════════════════════════════════════════════════════════
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKIP_BUILD=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --skip-build) SKIP_BUILD=true ;;
  esac
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         WAF Proxy Lab — Full Run Pipeline           ║"
echo "║                                                      ║"
echo "║  01. Build images                                   ║"
echo "║  02. Start containers                               ║"
echo "║  03. Setup DVWA database                            ║"
echo "║  04. Test WAF OFF (baseline)                        ║"
echo "║  05. Test WAF ON  (blocking)                        ║"
echo "║  06. Analyze logs                                   ║"
echo "║  07. Compare results                                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

STEP=0
step() {
  STEP=$((STEP+1))
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Bước $STEP: $1"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ── 01: Build ──────────────────────────────────────────────
if [ "$SKIP_BUILD" = false ]; then
  step "Build Docker images"
  bash "$ROOT/run/01_build.sh"
else
  echo "⏭ Bỏ qua build (--skip-build)"
fi

# ── 02: Start ─────────────────────────────────────────────
step "Khởi động lab"
bash "$ROOT/run/02_start.sh"

echo ""
echo "⏳ Chờ 15 giây để backend DVWA khởi động MySQL..."
sleep 15

# ── 03: Setup DVWA ────────────────────────────────────────
step "Khởi tạo DVWA database"
bash "$ROOT/run/03_setup_dvwa.sh"

sleep 3

# ── 04: Test WAF OFF ──────────────────────────────────────
step "Test với WAF ở DetectionOnly (baseline)"
bash "$ROOT/run/04_test_waf_off.sh"

sleep 2

# ── 05: Test WAF ON ───────────────────────────────────────
step "Test với WAF ở Blocking mode"
bash "$ROOT/run/05_test_waf_on.sh"

sleep 2

# ── 06: Analyze logs ──────────────────────────────────────
step "Phân tích log ModSecurity"
bash "$ROOT/run/06_analyze_logs.sh"

# ── 07: Compare ───────────────────────────────────────────
step "So sánh kết quả WAF OFF vs ON"
bash "$ROOT/run/07_compare.sh"

# ── Done ──────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              ✅ PIPELINE HOÀN THÀNH!                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Kết quả:"
echo "  ├── logs/results_off/      WAF OFF (baseline)"
echo "  ├── logs/results_on/       WAF ON  (blocking)"
echo "  ├── logs/export/           CSV + JSON tổng hợp"
echo "  └── logs/audit.log         Raw ModSecurity log"
echo ""
echo "  Dừng lab: bash run/08_stop.sh"
echo ""
