#!/usr/bin/env python3
"""
Free AI API Starter Kit — Endpoint Health Checker.
Re-test all configured endpoints and update the working config.

Usage:
    python3 check_endpoints.py
    python3 check_endpoints.py --update  # Update the config file
    python3 check_endpoints.py --json    # JSON output only
"""
import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
# Look in scripts/ or parent
if (SCRIPT_DIR / "endpoints.json").exists():
    ENDPOINTS_FILE = SCRIPT_DIR / "endpoints.json"
else:
    ENDPOINTS_FILE = SCRIPT_DIR.parent / "endpoints.json"
SETUP_DIR = SCRIPT_DIR / ".free_ai_setup"
if SCRIPT_DIR.name == "scripts":
    SETUP_DIR = SCRIPT_DIR.parent / ".free_ai_setup"
OUTPUT_JSON = SCRIPT_DIR.parent / "endpoints-status.json" if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR / "endpoints-status.json"

GREEN = "\033[92m"
YELLOW = "\033[33m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def c(color, text):
    print(f"{color}{text}{RESET}")


def load_endpoints():
    if not ENDPOINTS_FILE.exists():
        c(RED, f"endpoints.json not found at {ENDPOINTS_FILE}")
        sys.exit(1)
    with open(ENDPOINTS_FILE) as f:
        return json.load(f)


def test_endpoint(url, api_key=None, model=None, timeout=15):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = json.dumps({
        "model": model or "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
        "max_tokens": 10,
    }).encode()

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "status": "ok" if reply.strip() else "empty",
                "reply": reply,
                "latency_ms": resp.headers.get("X-RateLimit-Reset", "") or ""
            }
    except urllib.error.HTTPError as e:
        return {"status": "http_error", "status_code": e.code}
    except urllib.error.URLError as e:
        return {"status": "network", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Update the endpoints config")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    endpoints_data = load_endpoints()
    endpoints = endpoints_data.get("endpoints", [])

    if args.json:
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    total = len(endpoints)
    working = []
    issues = []

    if not args.json:
        c(BOLD, f"\n=== Free AI Endpoint Health Check ===")
        c(CYAN, f"Testing {total} endpoints...\n")

    for i, ep in enumerate(endpoints, 1):
        name = ep["name"]
        url = ep["url"]
        env = ep.get("api_key_env")
        api_key = os.environ.get(env, "") if env else ""

        if not api_key:
            if not args.json:
                c(YELLOW, f"  {i:3d}/{total}  {name[:42]:<42s} → needs key ({env})")
            issues.append({"name": name, "issue": "missing_key", "env": env})
            continue

        result = test_endpoint(url, api_key=api_key, model=ep.get("default_model"))
        entry = {"name": name, "provider": ep.get("provider", name.split(" - ")[0]), **result}

        if result["status"] == "ok":
            working.append(entry)
            if not args.json:
                c(GREEN, f"  {i:3d}/{total}  {name[:42]:<42s} → OK")
        else:
            if not args.json:
                c(YELLOW, f"  {i:3d}/{total}  {name[:42]:<42s} → {result.get('status', '?')}")
            issues.append({"name": name, "issue": result["status"]})

    if not args.json:
        c(BOLD, f"\n=== Results ===")
        c(GREEN, f"  Working: {len(working)} / {total}")
        if issues:
            c(YELLOW, f"  Issues:  {len(issues)}")
            print()
            for iss in issues:
                print(f"    - {iss['name']}: {iss['issue']}")
        print()

    if args.update:
        status_json = {
            "checked": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total": total,
            "working": len(working),
            "endpoints": working,
        }
        OUTPUT_JSON.write_text(json.dumps(status_json, indent=2))
        if not args.json:
            c(GREEN, f"  Updated {OUTPUT_JSON}")

    if args.json:
        sys.stdout = old_stdout
        print(json.dumps({"working": len(working), "total": total, "working_endpoints": working}, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
