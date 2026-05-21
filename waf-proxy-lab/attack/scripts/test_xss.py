#!/usr/bin/env python3
"""
test_xss.py — Kiểm thử XSS qua WAF
Người B viết | waf-proxy-lab

Dùng:
  python3 test_xss.py --target http://waf-server
  python3 test_xss.py --target http://waf-server --mode stored
"""

import requests
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    RED = Fore.RED; GREEN = Fore.GREEN; CYAN = Fore.CYAN
    RESET = Style.RESET_ALL; BOLD = Style.BRIGHT
except ImportError:
    RED = GREEN = CYAN = RESET = BOLD = ""


def load_payloads(filepath: str) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        print(f"{RED}[ERROR] Không tìm thấy: {filepath}{RESET}")
        sys.exit(1)
    return [l.strip() for l in path.read_text().splitlines()
            if l.strip() and not l.startswith("#")]


def test_reflected(target: str, payload: str) -> dict:
    """XSS Reflected — payload trong query string GET."""
    try:
        resp = requests.get(
            f"{target}/vulnerabilities/xss_r/",
            params={"name": payload},
            cookies={"security": "low", "PHPSESSID": "lab"},
            timeout=10,
        )
        return {
            "type": "reflected",
            "payload": payload,
            "status_code": resp.status_code,
            "blocked": resp.status_code == 403,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"type": "reflected", "payload": payload,
                "status_code": -1, "blocked": False, "note": str(e),
                "timestamp": datetime.now().isoformat()}


def test_stored(target: str, payload: str) -> dict:
    """XSS Stored — payload POST vào guestbook DVWA."""
    try:
        resp = requests.post(
            f"{target}/vulnerabilities/xss_s/",
            data={
                "txtName": "tester",
                "mtxMessage": payload,
                "btnSign": "Sign Guestbook",
            },
            cookies={"security": "low", "PHPSESSID": "lab"},
            timeout=10,
        )
        return {
            "type": "stored",
            "payload": payload,
            "status_code": resp.status_code,
            "blocked": resp.status_code == 403,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"type": "stored", "payload": payload,
                "status_code": -1, "blocked": False, "note": str(e),
                "timestamp": datetime.now().isoformat()}


def run(target: str, payloads: list[str],
        mode: str = "both", verbose: bool = False) -> list[dict]:
    results = []
    print(f"\n{BOLD}{CYAN}[XSS Test — {mode}]{RESET} Target: {target}")
    print(f"{'─'*55}")

    for payload in payloads:
        tests = []
        if mode in ("reflected", "both"):
            tests.append(test_reflected(target, payload))
        if mode in ("stored", "both"):
            tests.append(test_stored(target, payload))

        for r in tests:
            results.append(r)
            if verbose:
                icon = f"{GREEN}BLOCKED ✓{RESET}" if r["blocked"] else f"{RED}PASSED  ✗{RESET}"
                short = payload[:40].ljust(40)
                print(f"  [{icon}] [{r['type'][:3]}] {short}  ({r['status_code']})")

    blocked = sum(1 for r in results if r["blocked"])
    rate    = blocked / len(results) * 100 if results else 0
    print(f"{'─'*55}")
    print(f"  Tổng: {len(results)}  |  {GREEN}Blocked: {blocked}{RESET}  |  "
          f"{RED}Bypass: {len(results)-blocked}{RESET}  |  Phát hiện: {rate:.1f}%")
    return results


def main():
    parser = argparse.ArgumentParser(description="XSS test — waf-proxy-lab")
    parser.add_argument("--target", default="http://waf-server")
    parser.add_argument("--payload-file", default="/opt/attack/payloads/xss.txt")
    parser.add_argument("--mode", choices=["reflected", "stored", "both"],
                        default="both")
    parser.add_argument("--output", default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    payloads = load_payloads(args.payload_file)
    results  = run(args.target, payloads, args.mode, args.verbose)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n  ✓ Đã lưu: {args.output}")


if __name__ == "__main__":
    main()
