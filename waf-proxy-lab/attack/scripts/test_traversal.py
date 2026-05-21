#!/usr/bin/env python3
"""
test_traversal.py — Kiểm thử Path Traversal qua WAF
Người B viết | waf-proxy-lab
"""

import requests
import argparse
import json
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    RED = Fore.RED; GREEN = Fore.GREEN; CYAN = Fore.CYAN
    RESET = Style.RESET_ALL; BOLD = Style.BRIGHT
except ImportError:
    RED = GREEN = CYAN = RESET = BOLD = ""


def load_payloads(filepath):
    return [l.strip() for l in Path(filepath).read_text().splitlines()
            if l.strip() and not l.startswith("#")]


def test_traversal(target, payload):
    try:
        resp = requests.get(
            f"{target}/vulnerabilities/fi/",
            params={"page": payload},
            cookies={"security": "low", "PHPSESSID": "lab"},
            timeout=10,
        )
        # Kiểm tra thêm: nếu response chứa "root:" thì là bypass thực sự
        got_file = "root:" in resp.text and resp.status_code == 200
        return {
            "payload":     payload,
            "status_code": resp.status_code,
            "blocked":     resp.status_code == 403,
            "got_file":    got_file,
            "timestamp":   datetime.now().isoformat(),
        }
    except Exception as e:
        return {"payload": payload, "status_code": -1,
                "blocked": False, "got_file": False,
                "note": str(e), "timestamp": datetime.now().isoformat()}


def run(target, payloads, verbose=False):
    results = []
    print(f"\n{BOLD}{CYAN}[Path Traversal Test]{RESET} Target: {target}")
    print(f"{'─'*55}")

    for payload in payloads:
        r = test_traversal(target, payload)
        results.append(r)
        if verbose:
            if r["got_file"]:
                icon = f"{RED}FILE READ ✗✗{RESET}"
            elif r["blocked"]:
                icon = f"{GREEN}BLOCKED   ✓{RESET}"
            else:
                icon = f"{RED}PASSED    ✗{RESET}"
            print(f"  [{icon}] {payload[:45].ljust(45)}  ({r['status_code']})")

    blocked  = sum(1 for r in results if r["blocked"])
    got_file = sum(1 for r in results if r["got_file"])
    rate     = blocked / len(results) * 100 if results else 0
    print(f"{'─'*55}")
    print(f"  Tổng: {len(results)}  |  {GREEN}Blocked: {blocked}{RESET}  |  "
          f"{RED}File read: {got_file}{RESET}  |  Phát hiện: {rate:.1f}%")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="http://waf-server")
    parser.add_argument("--payload-file",
                        default="/opt/attack/payloads/path-traversal.txt")
    parser.add_argument("--output", default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    payloads = load_payloads(args.payload_file)
    results  = run(args.target, payloads, args.verbose)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
