#!/usr/bin/env python3
"""
parse_logs.py — Đọc và phân tích modsec_audit.log
Người A viết | waf-proxy-lab

Dùng:
  python3 parse_logs.py /var/log/modsec/audit.log
  python3 parse_logs.py /opt/logs/audit.log
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_modsec_log(filepath: str) -> list[dict]:
    """
    Đọc log JSON từ ModSecurity.
    Mỗi dòng là một JSON object độc lập.
    Bỏ qua dòng lỗi parse (log có thể bị cắt giữa chừng).
    """
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] Không tìm thấy log: {filepath}")
        sys.exit(1)

    entries = []
    for i, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            tx  = obj.get("transaction", obj)  # handle cả hai format
            entries.append(tx)
        except json.JSONDecodeError:
            continue  # bỏ qua dòng không parse được

    return entries


def analyze(entries: list[dict]) -> dict:
    stats = {
        "total":               len(entries),
        "rules_triggered":     Counter(),
        "attack_types":        Counter(),
        "attacker_ips":        Counter(),
        "top_uris":            Counter(),
        "severity_count":      Counter(),
        "hourly_distribution": Counter(),
        "anomaly_scores":      [],
        "bypassed_payloads":   [],  # entry có score > 0 nhưng không bị block
    }

    for tx in entries:
        ip  = tx.get("client_ip", "unknown")
        uri = tx.get("request", {}).get("uri", "")[:100]
        stats["attacker_ips"][ip]  += 1
        stats["top_uris"][uri]     += 1

        # Phân tích anomaly score
        scores = tx.get("anomaly_scores", {})
        in_score = scores.get("incoming_score", 0)
        if in_score:
            stats["anomaly_scores"].append(in_score)

        # Phân tích từng message/rule
        for msg in tx.get("messages", []):
            details  = msg.get("details", {})
            rule_id  = details.get("ruleId", "unknown")
            severity = details.get("severity", "unknown")
            rule_file = details.get("file", "")

            stats["rules_triggered"][rule_id] += 1
            stats["severity_count"][severity] += 1

            # Phân loại loại tấn công
            if "SQLI" in rule_file.upper():
                stats["attack_types"]["SQL Injection"] += 1
            elif "XSS" in rule_file.upper():
                stats["attack_types"]["XSS"] += 1
            elif "LFI" in rule_file.upper() or "RFI" in rule_file.upper():
                stats["attack_types"]["Path Traversal / LFI"] += 1
            elif "SSRF" in rule_file.upper():
                stats["attack_types"]["SSRF"] += 1
            elif "9001" <= rule_id <= "9099":
                stats["attack_types"]["Custom Rule"] += 1
            else:
                stats["attack_types"]["Other"] += 1

        # Phân phối theo giờ
        time_str = tx.get("time", "")
        if time_str:
            try:
                hour = datetime.fromisoformat(
                    time_str.replace("Z", "+00:00")
                ).hour
                stats["hourly_distribution"][f"{hour:02d}:00"] += 1
            except (ValueError, AttributeError):
                pass

    return stats


def print_report(stats: dict):
    SEP  = "=" * 52
    SEP2 = "─" * 52

    print(f"\n{SEP}")
    print(f"  ModSecurity Audit Log — Analysis Report")
    print(f"{SEP}")

    print(f"\n📊  Tổng request bị block: {stats['total']}")

    if stats["anomaly_scores"]:
        avg = sum(stats["anomaly_scores"]) / len(stats["anomaly_scores"])
        mx  = max(stats["anomaly_scores"])
        print(f"    Anomaly score  avg={avg:.1f}  max={mx}")

    print(f"\n{SEP2}")
    print(f"🎯  Loại tấn công")
    print(f"{SEP2}")
    for attack, count in stats["attack_types"].most_common():
        bar  = "█" * min(count, 25)
        pct  = count / stats["total"] * 100 if stats["total"] else 0
        print(f"  {attack:<28} {count:>4}  ({pct:4.1f}%)  {bar}")

    print(f"\n{SEP2}")
    print(f"🔴  Severity")
    print(f"{SEP2}")
    for sev, count in stats["severity_count"].most_common():
        print(f"  {sev:<20} {count:>4}")

    print(f"\n{SEP2}")
    print(f"📋  Top 10 rule được kích hoạt")
    print(f"{SEP2}")
    for rule, count in stats["rules_triggered"].most_common(10):
        print(f"  Rule {rule:<12} {count:>4} lần")

    print(f"\n{SEP2}")
    print(f"🌐  Top attacker IPs")
    print(f"{SEP2}")
    for ip, count in stats["attacker_ips"].most_common(5):
        print(f"  {ip:<22} {count:>4} request")

    print(f"\n{SEP2}")
    print(f"🔗  Top URI bị tấn công")
    print(f"{SEP2}")
    for uri, count in stats["top_uris"].most_common(5):
        print(f"  {uri[:50]:<50}  {count:>4}")

    if stats["hourly_distribution"]:
        print(f"\n{SEP2}")
        print(f"🕐  Phân phối theo giờ")
        print(f"{SEP2}")
        for hour in sorted(stats["hourly_distribution"]):
            count = stats["hourly_distribution"][hour]
            bar   = "▪" * min(count, 30)
            print(f"  {hour}  {bar} {count}")

    print(f"\n{SEP}\n")


if __name__ == "__main__":
    logfile = sys.argv[1] if len(sys.argv) > 1 else "/var/log/modsec/audit.log"
    print(f"[parse_logs] Đọc: {logfile}")
    entries = parse_modsec_log(logfile)
    if not entries:
        print("Log rỗng. Hãy chạy lab và thực hiện tấn công trước.")
        sys.exit(0)
    stats = analyze(entries)
    print_report(stats)
