#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/01_build.sh — Bước 1: Build tất cả Docker images
# Chạy từ thư mục gốc repo: bash run/01_build.sh
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 1: Build Images   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "[1/3] Build waf-server (Nginx + ModSecurity)..."
docker build \
  --file infra/waf-server/Dockerfile \
  --tag waf-server:latest \
  --no-cache \
  . \
  && echo "  ✓ waf-server built"

echo ""
echo "[2/3] Build backend (DVWA)..."
docker build \
  --file infra/backend/Dockerfile \
  --tag waf-backend:latest \
  . \
  && echo "  ✓ waf-backend built"

echo ""
echo "[3/3] Build attacker (Kali)..."
docker build \
  --file infra/attacker/Dockerfile \
  --tag waf-attacker:latest \
  . \
  && echo "  ✓ waf-attacker built"

echo ""
echo "✅ Tất cả images đã được build."
echo "   Chạy tiếp: bash run/02_start.sh"
