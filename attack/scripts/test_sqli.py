#!/usr/bin/env python3
"""
test_sqli.py — Kiểm thử SQL Injection qua WAF
Người B viết | waf-proxy-lab

Dùng:
  python3 test_sqli.py --target http://waf-server
  python3 test_sqli.py --target http://waf-server --verbose
  python3 test_sqli.py --target http://waf-server --output results/sqli.json
"""

import requests
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Màu terminal ─────────────────────────────────────────
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    RED   = Fore.RED
    GREEN = Fore.GREEN
    CYAN  = Fore.CYAN
    RESET = Style.RESET_ALL
    BOLD  = Style.BRIGHT
except ImportError:
    RED = GREEN = CYAN = RESET = BOLD = ""


def load_payloads(filepath: str) -> list[str]:
    """Đọc payload từ file, bỏ comment và dòng trống."""
    path = Path(filepath)
    if not path.exists():
        print(f"{RED}[ERROR] Không tìm thấy file: {filepath}{RESET}")
        sys.exit(1)
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def send_request(target: str, payload: str, timeout: int = 10) -> dict:
    """Gửi một request SQLi và trả về kết quả."""
    endpoint = f"{target}/vulnerabilities/sqli/"
    start = time.time()
    try:
        resp = requests.get(
            endpoint,
            params={"id": payload, "Submit": "Submit"},
            cookies={"security": "low", "PHPSESSID": "lab"},
            timeout=timeout,
            allow_redirects=True,
        )
        elapsed = time.time() - start
        return {
            "payload":     payload,
            "status_code": resp.status_code,
            "blocked":     resp.status_code == 403,
            "elapsed_s":   round(elapsed, 3),
            "note":        "",
            "timestamp":   datetime.now().isoformat(),
        }
    except requests.Timeout:
        elapsed = time.time() - start
        # Timeout trên time-based payload → có thể bị chặn hoặc SLEEP thực thi
        return {
            "payload":     payload,
            "status_code": 0,
            "blocked":     elapsed < timeout * 0.9,  # nhanh hơn timeout → bị block
            "elapsed_s":   round(elapsed, 3),
            "note":        "timeout",
            "timestamp":   datetime.now().isoformat(),
        }
    except requests.ConnectionError as e:
        return {
            "payload":     payload,
            "status_code": -1,
            "blocked":     False,
            "elapsed_s":   0,
            "note":        f"connection error: {e}",
            "timestamp":   datetime.now().isoformat(),
        }


def run(target: str, payloads: list[str], verbose: bool = False) -> list[dict]:
    results = []
    print(f"\n{BOLD}{CYAN}[SQLi Test]{RESET} Target: {target}")
    print(f"{'─'*55}")

    for payload in payloads:
        result = send_request(target, payload)
        results.append(result)

        if verbose:
            if result["blocked"]:
                icon = f"{GREEN}BLOCKED ✓{RESET}"
            else:
                icon = f"{RED}PASSED  ✗{RESET}"
            short = payload[:45].ljust(45)
            print(f"  [{icon}] {short}  ({result['status_code']}, {result['elapsed_s']}s)")

    blocked = sum(1 for r in results if r["blocked"])
    passed  = len(results) - blocked
    rate    = blocked / len(results) * 100 if results else 0

    print(f"{'─'*55}")
    print(f"  Tổng: {len(results)} payload  |  "
          f"{GREEN}Blocked: {blocked}{RESET}  |  "
          f"{RED}Bypass: {passed}{RESET}  |  "
          f"Phát hiện: {rate:.1f}%")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="SQLi test script — waf-proxy-lab"
    )
    parser.add_argument("--target",
                        default="http://waf-server",
                        help="URL WAF server (default: http://waf-server)")
    parser.add_argument("--payload-file",
                        default="/opt/attack/payloads/sqli.txt",
                        help="Đường dẫn file payload")
    parser.add_argument("--output",
                        default=None,
                        help="Lưu kết quả JSON ra file")
    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="In chi tiết từng payload")
    args = parser.parse_args()

    payloads = load_payloads(args.payload_file)
    results  = run(args.target, payloads, args.verbose)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n  ✓ Đã lưu: {args.output}")

    return results


if __name__ == "__main__":
    main()
