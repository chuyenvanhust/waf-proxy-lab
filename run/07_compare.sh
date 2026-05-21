#!/bin/bash
# ─────────────────────────────────────────────────────────
# run/07_compare.sh — Bước 7: So sánh kết quả WAF ON vs OFF
# ─────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OFF="$ROOT/logs/results_off"
ON="$ROOT/logs/results_on"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  WAF Proxy Lab — Bước 7: So sánh kết quả   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

python3 - <<'PYEOF'
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent if '__file__' in dir() else Path('.')

# Tìm thư mục results
# Khi chạy từ bash, ROOT sẽ được truyền qua env
import os
ROOT = Path(os.environ.get('ROOT', '.'))
OFF  = ROOT / 'logs' / 'results_off'
ON   = ROOT / 'logs' / 'results_on'

categories = [
    ('SQLi',           'sqli.json'),
    ('XSS',            'xss.json'),
    ('Path Traversal', 'traversal.json'),
]

SEP  = '═' * 58
SEP2 = '─' * 58

print(f'\n{SEP}')
print(f'  So sánh: WAF OFF vs WAF ON')
print(f'{SEP}')
print(f'  {"Kịch bản":<20} {"WAF OFF":>10} {"WAF ON":>10} {"Cải thiện":>12}')
print(f'{SEP2}')

total_off = total_on = total_payloads = 0

for label, fname in categories:
    off_file = OFF / fname
    on_file  = ON  / fname

    if not off_file.exists() or not on_file.exists():
        print(f'  {label:<20} {"(chưa có dữ liệu)":>34}')
        continue

    off_data = json.loads(off_file.read_text())
    on_data  = json.loads(on_file.read_text())

    off_blocked = sum(1 for r in off_data if r.get('blocked'))
    on_blocked  = sum(1 for r in on_data  if r.get('blocked'))
    n = len(on_data)

    off_pct = off_blocked / n * 100 if n else 0
    on_pct  = on_blocked  / n * 100 if n else 0
    delta   = on_pct - off_pct

    total_off      += off_blocked
    total_on       += on_blocked
    total_payloads += n

    arrow = '↑' if delta > 0 else ('↓' if delta < 0 else '=')
    print(f'  {label:<20} {off_pct:>8.1f}%  {on_pct:>8.1f}%  '
          f'{arrow} {abs(delta):>6.1f}%')

print(f'{SEP2}')
if total_payloads:
    off_total_pct = total_off / total_payloads * 100
    on_total_pct  = total_on  / total_payloads * 100
    print(f'  {"TỔNG":<20} {off_total_pct:>8.1f}%  {on_total_pct:>8.1f}%'
          f'  ↑ {on_total_pct - off_total_pct:>5.1f}%')

# False positive
fp_file = ON / 'false_positive.json'
if fp_file.exists():
    fp_data = json.loads(fp_file.read_text())
    fp_count = sum(1 for r in fp_data if r.get('false_positive'))
    fp_total = len(fp_data)
    print(f'\n  False Positive  : {fp_count}/{fp_total} '
          f'({fp_count/fp_total*100:.1f}% request hợp lệ bị chặn nhầm)')

print(f'\n{SEP}')
print(f'  Kết quả lưu tại: logs/results_on/ và logs/results_off/')
print(f'{SEP}\n')
PYEOF

export ROOT
python3 - <<'PYEOF'
import os, json
from pathlib import Path
ROOT = Path(os.environ.get('ROOT', '.'))
OFF  = ROOT / 'logs' / 'results_off'
ON   = ROOT / 'logs' / 'results_on'

categories = [('SQLi','sqli.json'),('XSS','xss.json'),('Path Traversal','traversal.json')]
SEP  = '═' * 58
SEP2 = '─' * 58

print(f'\n{SEP}')
print(f'  So sánh: WAF OFF vs WAF ON')
print(f'{SEP}')
print(f'  {"Kịch bản":<20} {"WAF OFF":>10} {"WAF ON":>10} {"Cải thiện":>12}')
print(f'{SEP2}')

total_off = total_on = total_payloads = 0
for label, fname in categories:
    off_file = OFF / fname
    on_file  = ON  / fname
    if not off_file.exists() or not on_file.exists():
        print(f'  {label:<20} {"(chưa có dữ liệu)":>34}')
        continue
    off_data = json.loads(off_file.read_text())
    on_data  = json.loads(on_file.read_text())
    off_blocked = sum(1 for r in off_data if r.get('blocked'))
    on_blocked  = sum(1 for r in on_data  if r.get('blocked'))
    n = len(on_data)
    off_pct = off_blocked/n*100 if n else 0
    on_pct  = on_blocked/n*100  if n else 0
    delta   = on_pct - off_pct
    total_off += off_blocked; total_on += on_blocked; total_payloads += n
    arrow = '↑' if delta>0 else ('↓' if delta<0 else '=')
    print(f'  {label:<20} {off_pct:>8.1f}%  {on_pct:>8.1f}%  {arrow} {abs(delta):>6.1f}%')

print(f'{SEP2}')
if total_payloads:
    op = total_off/total_payloads*100
    np = total_on/total_payloads*100
    print(f'  {"TỔNG":<20} {op:>8.1f}%  {np:>8.1f}%  ↑ {np-op:>5.1f}%')

fp_file = ON/'false_positive.json'
if fp_file.exists():
    fp_data = json.loads(fp_file.read_text())
    fc = sum(1 for r in fp_data if r.get('false_positive'))
    ft = len(fp_data)
    print(f'\n  False Positive: {fc}/{ft} ({fc/ft*100:.1f}% request hợp lệ bị chặn nhầm)')
print(f'\n{SEP}\n')
PYEOF

echo "✅ So sánh hoàn thành!"
echo "   Chạy tiếp: bash run/08_stop.sh (khi xong lab)"
