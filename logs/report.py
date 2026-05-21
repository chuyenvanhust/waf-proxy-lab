#!/usr/bin/env python3
"""
report.py — Xuất báo cáo tổng hợp từ modsec_audit.log
Người A viết | waf-proxy-lab

Dùng:
  python3 report.py
  python3 report.py --log /opt/logs/audit.log --csv report.csv
"""

import csv
import json
import argparse
import sys
from pathlib import Path

# Import từ cùng thư mục
sys.path.insert(0, str(Path(__file__).parent))
from parse_logs import parse_modsec_log, analyze, print_report


def export_csv(entries: list[dict], output_path: str):
    """Xuất từng entry ra CSV để import vào Excel / Google Sheets."""
    fieldnames = [
        "timestamp", "client_ip", "method", "uri",
        "rule_id", "severity", "attack_type",
        "anomaly_score", "message",
    ]

    rows = []
    for tx in entries:
        ip     = tx.get("client_ip", "")
        uri    = tx.get("request", {}).get("uri", "")
        method = tx.get("request", {}).get("method", "")
        time   = tx.get("time", "")
        scores = tx.get("anomaly_scores", {})
        score  = scores.get("incoming_score", 0)

        messages = tx.get("messages", [])
        if not messages:
            rows.append({
                "timestamp": time, "client_ip": ip,
                "method": method, "uri": uri,
                "rule_id": "", "severity": "",
                "attack_type": "", "anomaly_score": score,
                "message": "",
            })
        else:
            for msg in messages:
                details     = msg.get("details", {})
                rule_id     = details.get("ruleId", "")
                severity    = details.get("severity", "")
                rule_file   = details.get("file", "")
                message_str = msg.get("message", "")

                # Phân loại
                if "SQLI" in rule_file.upper():
                    attack_type = "SQL Injection"
                elif "XSS" in rule_file.upper():
                    attack_type = "XSS"
                elif "LFI" in rule_file.upper():
                    attack_type = "Path Traversal"
                else:
                    attack_type = "Other"

                rows.append({
                    "timestamp":   time,
                    "client_ip":   ip,
                    "method":      method,
                    "uri":         uri[:100],
                    "rule_id":     rule_id,
                    "severity":    severity,
                    "attack_type": attack_type,
                    "anomaly_score": score,
                    "message":     message_str[:120],
                })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Đã xuất CSV ({len(rows)} dòng): {output_path}")


def export_summary_json(stats: dict, output_path: str):
    """Xuất stats tổng hợp ra JSON."""
    # Convert Counter → dict để JSON serialize
    export = {k: dict(v) if hasattr(v, "most_common") else v
              for k, v in stats.items()}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"✓ Đã xuất JSON summary: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="WAF Lab Report Generator"
    )
    parser.add_argument("--log",
                        default="/var/log/modsec/audit.log",
                        help="Đường dẫn modsec_audit.log")
    parser.add_argument("--csv",
                        default=None,
                        help="Xuất CSV (vd: logs/report.csv)")
    parser.add_argument("--json-summary",
                        default=None,
                        help="Xuất JSON summary (vd: logs/summary.json)")
    parser.add_argument("--no-print",
                        action="store_true",
                        help="Không in báo cáo ra console")
    args = parser.parse_args()

    print(f"[report] Đọc log: {args.log}")
    entries = parse_modsec_log(args.log)

    if not entries:
        print("Log rỗng. Hãy chạy các kịch bản tấn công trước.")
        return

    stats = analyze(entries)

    if not args.no_print:
        print_report(stats)

    if args.csv:
        export_csv(entries, args.csv)

    if args.json_summary:
        export_summary_json(stats, args.json_summary)


if __name__ == "__main__":
    main()
