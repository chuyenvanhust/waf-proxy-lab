#!/usr/bin/env python3
"""
test_normal.py — Đo False Positive (WAF chặn nhầm request hợp lệ)
Người B viết | waf-proxy-lab
"""

import requests
import json
from datetime import datetime
from pathlib import Path
import argparse

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    RED = Fore.RED; GREEN = Fore.GREEN; CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW; RESET = Style.RESET_ALL; BOLD = Style.BRIGHT
except ImportError:
    RED = GREEN = CYAN = YELLOW = RESET = BOLD = ""


# ── Danh sách request hợp lệ cần test ────────────────────
NORMAL_REQUESTS = [
    {
        "desc": "Home page GET",
        "method": "GET",
        "path": "/",
        "params": {},
        "data": {},
    },
    {
        "desc": "Login bình thường",
        "method": "POST",
        "path": "/login.php",
        "params": {},
        "data": {"username": "admin", "password": "password", "Login": "Login"},
    },
    {
        "desc": "Tên có dấu nháy (O'Brien)",
        "method": "GET",
        "path": "/vulnerabilities/xss_r/",
        "params": {"name": "O'Brien"},
        "data": {},
    },
    {
        "desc": "Ampersand trong content",
        "method": "GET",
        "path": "/vulnerabilities/xss_r/",
        "params": {"name": "Tom & Jerry"},
        "data": {},
    },
    {
        "desc": "Từ khóa JS trong search",
        "method": "GET",
        "path": "/",
        "params": {"search": "learn javascript programming"},
        "data": {},
    },
    {
        "desc": "ID số nguyên bình thường",
        "method": "GET",
        "path": "/vulnerabilities/sqli/",
        "params": {"id": "1", "Submit": "Submit"},
        "data": {},
    },
    {
        "desc": "Upload page GET",
        "method": "GET",
        "path": "/vulnerabilities/upload/",
        "params": {},
        "data": {},
    },
]


def run(target: str, verbose: bool = True) -> list[dict]:
    results = []
    print(f"\n{BOLD}{CYAN}[False Positive Test]{RESET} Target: {target}")
    print(f"{'─'*60}")

    for req in NORMAL_REQUESTS:
        url = target + req["path"]
        try:
            resp = requests.request(
                req["method"], url,
                params=req["params"],
                data=req["data"],
                cookies={"security": "low", "PHPSESSID": "lab"},
                timeout=10,
                allow_redirects=True,
            )
            is_fp = resp.status_code == 403
            result = {
                "desc":        req["desc"],
                "method":      req["method"],
                "path":        req["path"],
                "status_code": resp.status_code,
                "false_positive": is_fp,
                "timestamp":   datetime.now().isoformat(),
            }
        except Exception as e:
            result = {
                "desc": req["desc"], "method": req["method"],
                "path": req["path"], "status_code": -1,
                "false_positive": False, "note": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        results.append(result)

        if verbose:
            if result["false_positive"]:
                icon = f"{RED}✗ FALSE POSITIVE{RESET}"
            else:
                icon = f"{GREEN}✓ OK            {RESET}"
            desc = req["desc"].ljust(35)
            print(f"  [{icon}]  {desc}  ({result['status_code']})")

    fp_count = sum(1 for r in results if r["false_positive"])
    total    = len(results)
    fp_rate  = fp_count / total * 100 if total else 0

    print(f"{'─'*60}")
    if fp_count == 0:
        print(f"  {GREEN}False Positive: 0/{total} (0%) — Tốt!{RESET}")
    else:
        print(f"  {YELLOW}False Positive: {fp_count}/{total} ({fp_rate:.1f}%)"
              f" — Cân nhắc tăng anomaly threshold{RESET}")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="http://waf-server")
    parser.add_argument("--output", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", default=True)
    args = parser.parse_args()

    results = run(args.target, args.verbose)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n  ✓ Đã lưu: {args.output}")


if __name__ == "__main__":
    main()
