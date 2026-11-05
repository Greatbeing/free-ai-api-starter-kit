#!/usr/bin/env python3
"""
Free AI API Starter Kit — Quickstart Script
One command to discover, test, and configure free AI endpoints.
"""
import json
import sys
import urllib.request
import urllib.error
import os
import subprocess
import socket
import time
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
# endpoints.json can be in scripts/ or in the parent product dir
if (SCRIPT_DIR / "endpoints.json").exists():
    ENDPOINTS_FILE = SCRIPT_DIR / "endpoints.json"
else:
    ENDPOINTS_FILE = SCRIPT_DIR.parent / "endpoints.json"
SETUP_DIR = SCRIPT_DIR / ".free_ai_setup"
# Also set up in product root if script is in scripts/ subdirectory
if SCRIPT_DIR.name == "scripts":
    SETUP_DIR = SCRIPT_DIR.parent / ".free_ai_setup"

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[33m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def color_print(color, text):
    print(f"{color}{text}{RESET}")

def test_endpoint(url, api_key=None, model=None, timeout=10):
    """Test an API endpoint. Returns dict with result."""
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = json.dumps({
        "model": model or "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello in one word."}],
        "max_tokens": 10,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if reply.strip():
                return {"status": "ok", "reply": reply, "status_code": resp.status}
            else:
                return {"status": "empty", "status_code": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": "http_error", "status_code": e.code, "error": str(e)}
    except urllib.error.URLError as e:
        return {"status": "network", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def load_endpoints():
    if ENDPOINTS_FILE.exists():
        with open(ENDPOINTS_FILE) as f:
            return json.load(f)
    return {"endpoints": [], "providers": []}

def print_banner():
    color_print(CYAN, f"""
{BOLD}╔══════════════════════════════════════════════════════════╗
║  Free AI API Starter Kit — Setup                          ║
║  Discovering thousands of free AI endpoints               ║
╚══════════════════════════════════════════════════════════╝
{RESET}""")

def test_all(endpoints_data):
    """Test all endpoints. Return working ones."""
    working = []
    endpoints = endpoints_data.get("endpoints", [])
    total = len(endpoints)

    color_print(BOLD, f"\nTesting {total} endpoints...\n")

    for i, ep in enumerate(endpoints, 1):
        url = ep["url"]
        api_key_env = ep.get("api_key_env")
        api_key = os.environ.get(api_key_env, "") if api_key_env else ""
        model = ep.get("default_model")

        status = ep.get("status", "unknown")
        if status == "requires_key" and not api_key:
            color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → needs key: {api_key_env}")
            continue

        result = test_endpoint(url, api_key, model)
        if result["status"] == "ok":
            color_print(GREEN, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → OK ✓")
            working.append({**ep, **result})
        elif result["status"] == "empty":
            color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → empty response ⚠️")
        elif result["status"] == "http_error":
            code = result["status_code"]
            if code == 429:
                color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → rate limited 🔄")
            elif code == 401:
                color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → auth needed 🔑")
            elif code in (403, 404):
                color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → not available ({code}) ✗")
            else:
                color_print(YELLOW, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → {code} ✗")
        else:
            color_print(RED, f"  {i:3d}/{total} {ep['name'][:40]:<40s} → {result['status']} ✗")

    return working

def save_setup(working):
    SETUP_DIR.mkdir(exist_ok=True)
    working_file = SETUP_DIR / "working_endpoints.json"
    with open(working_file, "w") as f:
        json.dump(working, f, indent=2)
    color_print(GREEN, f"\n✓ {len(working)} working endpoints saved to {working_file}\n")

def print_config_help(working):
    if not working:
        color_print(YELLOW, "No working endpoints found without API keys.\n")
        color_print(BOLD, "What to do next:\n")
        print("""
1. Sign up for free at these providers (no credit card needed):
   - https://openrouter.ai    → free models, $0 credit
   - https://huggingface.co   → free inference API
   - https://aistudio.google  → free Gemini API keys
   - https://console.groq.com → free Groq API keys

2. Save the API keys as environment variables:
   export OPENROUTER_API_KEY="your-key"
   export HF_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"

3. Re-run this script:  python3 quickstart.py
    """)
        return

    color_print(BOLD, "\n✓ Discovery complete!\n")
    print(f"  {len(working)} free AI endpoints are working for you right now.\n")
    color_print(BOLD, "Option A — Use in any OpenAI-compatible tool:\n")
    print("  Start the local proxy (next step) and point your tool at it.\n")
    color_print(BOLD, "Option B — Call directly:\n")
    for ep in working[:3]:
        print(f"    curl {ep['url']} ...  # {ep['name']}")
    print("")

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def start_local_proxy(working, port):
    """Start a simple OpenAI-compatible proxy."""
    # local_proxy.py can be in scripts/ or in the parent product dir
    if (SCRIPT_DIR / "local_proxy.py").exists():
        proxy_script = SCRIPT_DIR / "local_proxy.py"
    elif (SCRIPT_DIR.parent / "scripts" / "local_proxy.py").exists():
        proxy_script = SCRIPT_DIR.parent / "scripts" / "local_proxy.py"
    elif (SCRIPT_DIR.parent / "local_proxy.py").exists():
        proxy_script = SCRIPT_DIR.parent / "local_proxy.py"
    else:
        color_print(YELLOW, f"Local proxy script not found at {proxy_script}")
        color_print(BOLD, "Download local_proxy.py from the product bundle to use this feature.\n")
        return

    color_print(BOLD, f"\nStarting local AI proxy on port {port}...\n")
    print("  Press Ctrl+C to stop.\n")
    subprocess.run([sys.executable, str(proxy_script), "--port", str(port),
                    "--config", str(SETUP_DIR / "working_endpoints.json")])

def main():
    parser = argparse.ArgumentParser(description="Free AI API Starter Kit — Quickstart")
    parser.add_argument("--test-only", action="store_true", help="Test endpoints without starting proxy")
    parser.add_argument("--proxy-port", type=int, default=8080, help="Port for local proxy (default: 8080)")
    parser.add_argument("--no-proxy", action="store_true", help="Don't start the local proxy")
    args = parser.parse_args()

    print_banner()

    print(f"  Python: {sys.version}")
    print(f"  Script dir: {SCRIPT_DIR}")
    print(f"  Endpoints file: {ENDPOINTS_FILE}")
    if not ENDPOINTS_FILE.exists():
        color_print(RED, f"\n✗ endpoints.json not found at {ENDPOINTS_FILE}")
        color_print(RED, "  Make sure you're running from the product directory.\n")
        sys.exit(1)

    endpoints_data = load_endpoints()

    # Show configured API keys
    keys_configured = []
    keys_needed = []
    for ep in endpoints_data.get("endpoints", []):
        env = ep.get("api_key_env")
        if env:
            if os.environ.get(env):
                keys_configured.append(env)
            else:
                keys_needed.append(env)

    if keys_configured:
        color_print(GREEN, f"\n  API keys configured: {', '.join(keys_configured)}")
    if keys_needed:
        color_print(YELLOW, f"  API keys not set (some endpoints won't be testable): {', '.join(keys_needed)}")

    working = test_all(endpoints_data)
    save_setup(working)
    print_config_help(working)

    if args.test_only or args.no_proxy:
        return 0

    if not working:
        print("\nNo proxy to start. Fix your API keys first.\n")
        return 1

    if check_port(args.proxy_port):
        color_print(YELLOW, f"Port {args.proxy_port} is already in use.")
        color_print(YELLOW, "Use --proxy-port to pick a different port.\n")
        return 1

    start_local_proxy(working, args.proxy_port)
    return 0

if __name__ == "__main__":
    sys.exit(main())
