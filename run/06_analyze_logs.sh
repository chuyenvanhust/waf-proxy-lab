#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/06_analyze_logs.sh — Bước 6: Phân tích log WAF
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/logs/audit.log"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 6: Phân tích Log      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

if [ ! -f "$LOG" ] || [ ! -s "$LOG" ]; then
  echo "⚠ Log file rỗng hoặc không tồn tại: $LOG"
  echo "  Hãy chạy bước 04 và 05 trước."
  exit 1
fi

echo "[1/3] Thống kê log..."
LINE_COUNT=$(wc -l < "$LOG")
echo "  Log có $LINE_COUNT dòng"

echo ""
echo "[2/3] Báo cáo chi tiết..."
python3 "$ROOT/logs/parse_logs.py" "$LOG"

echo ""
echo "[3/3] Xuất CSV để dùng trong báo cáo Word..."
mkdir -p "$ROOT/logs/export"
python3 "$ROOT/logs/report.py" \
  --log "$LOG" \
  --csv "$ROOT/logs/export/waf_log_report.csv" \
  --json-summary "$ROOT/logs/export/summary.json" \
  --no-print

echo ""
echo "✅ Phân tích hoàn thành!"
echo "   CSV  : logs/export/waf_log_report.csv"
echo "   JSON : logs/export/summary.json"
echo ""
echo "   Chạy tiếp: bash run/07_compare.sh"
