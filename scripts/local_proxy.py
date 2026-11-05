#!/usr/bin/env python3
"""
Free AI API Starter Kit — Local Proxy
OpenAI-compatible endpoint that routes to free AI APIs.
Use with any OpenAI-compatible client.

Usage:
    python3 local_proxy.py --port 8080
    python3 local_proxy.py --port 8080 --config .free_ai_setup/working_endpoints.json

Point your OpenAI-compatible client to:
    http://localhost:8080/v1/chat/completions
    http://localhost:8080/v1/models
"""
import json
import sys
import time
import argparse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
# If script lives in scripts/, look in parent for config
if SCRIPT_DIR.name == "scripts":
    PRODUCT_ROOT = SCRIPT_DIR.parent
else:
    PRODUCT_ROOT = SCRIPT_DIR
DEFAULT_CONFIG = PRODUCT_ROOT / ".free_ai_setup" / "working_endpoints.json"


class FreeAIProxyHandler(BaseHTTPRequestHandler):
    """OpenAI-compatible proxy that routes to free AI endpoints."""

    proxy_config = []
    request_count = 0
    error_count = 0
    started_at = time.time()

    @classmethod
    def load_config(cls, config_path):
        """Load working endpoints configuration."""
        if not config_path.exists():
            print(f"[proxy] Config not found: {config_path}")
            print(f"[proxy] Run quickstart.py first to generate configuration.")
            cls.proxy_config = []
            return
        with open(config_path) as f:
            config = json.load(f)
        cls.proxy_config = config

        # Group endpoints by provider for better model routing
        cls.endpoints = {}
        for ep in config:
            provider = ep.get("provider", ep["name"].split(" - ")[0])
            if provider not in cls.endpoints:
                cls.endpoints[provider] = []
            cls.endpoints[provider].append(ep)

        print(f"[proxy] Loaded {len(config)} endpoints from {len(cls.endpoints)} providers")
        for provider, eps in cls.endpoints.items():
            print(f"[proxy]   {provider}: {len(eps)} endpoints")

    def _send_json(self, data, status=200):
        """Send JSON response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Handle GET requests for /v1/models and health check."""
        if self.path == "/v1/models":
            models = []
            for provider, eps in self.endpoints.items():
                for ep in eps:
                    model_id = ep.get("default_model", ep["name"])
                    models.append({
                        "id": f"{provider}/{model_id}",
                        "object": "model",
                        "created": int(self.started_at),
                        "owned_by": provider,
                        "root": f"{provider}/{model_id}",
                    })
            self._send_json({"object": "list", "data": models})
        elif self.path == "/health":
            uptime = int(time.time() - self.started_at)
            self._send_json({
                "status": "ok",
                "uptime_seconds": uptime,
                "endpoints": len(self.proxy_config),
                "providers": len(self.endpoints),
                "requests": self.request_count,
                "errors": self.error_count,
            })
        elif self.path == "/":
            self._send_json({
                "service": "Free AI API Starter Kit — Local Proxy",
                "version": "1.0.0",
                "docs": "/health, /v1/models, POST /v1/chat/completions",
                "config": str(DEFAULT_CONFIG),
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        """Handle POST requests for /v1/chat/completions."""
        if self.path != "/v1/chat/completions":
            self._send_json({"error": "not found"}, 404)
            return

        # Parse request body
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json({"error": f"invalid JSON: {e}"}, 400)
            return

        model = request.get("model", "")
        messages = request.get("messages", [])
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 1000)

        # Route to appropriate endpoint
        # Try to match the model name to a provider, otherwise use first available
        provider = self._route(model)
        if not provider:
            self._send_json({"error": "no available endpoints"}, 503)
            return

        endpoint = self.endpoints[provider][0]  # Use first endpoint of the provider
        result = self._forward(endpoint, model, messages, temperature, max_tokens)

        if result:
            self.request_count += 1
            response_body = result.get("response", "no response")
            usage = result.get("usage", {})
            self._send_json({
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": response_body},
                    "finish_reason": "stop",
                }],
                "usage": usage,
                "provider": provider,
            })
        else:
            self.error_count += 1
            self._send_json({
                "error": {
                    "message": result.get("error", "request failed") if result else "no endpoints available",
                    "type": "proxy_error",
                }
            }, 502)

    def _route(self, model):
        """Pick the best provider for this model or request."""
        if not self.proxy_config:
            return None

        # Parse model name: provider/model-name or just model-name
        model_clean = model.split("/")[-1].lower().replace("-", "").replace("_", "").replace(".", "")

        # Try to find a matching provider by model name
        for provider, eps in self.endpoints.items():
            for ep in eps:
                ep_model = ep.get("default_model", "")
                ep_model_clean = ep_model.lower().replace("-", "").replace("_", "").replace(".", "")
                if ep_model_clean and model_clean and (model_clean in ep_model_clean or ep_model_clean in model_clean):
                    return provider

        # Default: return first provider with an endpoint that needs no key
        # Or: return first provider overall
        if self.endpoints:
            return next(iter(self.endpoints.keys()))

        return None

    def _forward(self, endpoint, model, messages, temperature, max_tokens):
        """Forward the request to the actual AI endpoint."""
        # Normalize the model name
        model = self._normalize_model(endpoint, model)

        # Prepare the request body
        forward_body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if "stream" in json.dumps(messages).lower() or True:
            forward_body["stream"] = False

        headers = {
            "Content-Type": "application/json",
        }
        env = endpoint.get("api_key_env")
        api_key = os.environ.get(env, "") if env else ""
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Handle Gemini API format transformation if needed
        url = endpoint["url"]
        if "gemini" in url.lower() or "googleapis" in url:
            # Gemini uses a different API format
            model_name = endpoint.get("default_model", model)
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            gemini_body = {
                "contents": [{"parts": [{"text": msg["content"]}]} for msg in messages],
                "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
            }
            req = urllib.request.Request(
                gemini_url,
                data=json.dumps(gemini_body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        else:
            req = urllib.request.Request(
                url,
                data=json.dumps(forward_body).encode("utf-8"),
                headers=headers,
                method="POST",
            )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Extract response
            if "gemini" in url.lower() or "googleapis" in url:
                reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            else:
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})

            return {"response": reply, "usage": usage}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            return {"error": f"HTTP {e.code} from {url}: {error_body[:200]}"}
        except urllib.error.URLError as e:
            return {"error": f"Network error: {e.reason}"}
        except Exception as e:
            return {"error": f"Error: {e}"}

    def _normalize_model(self, endpoint, model):
        """Normalize the model name for the endpoint."""
        default = endpoint.get("default_model")
        if default:
            return default
        return model

    def log_message(self, format, *args):
        """Custom logging."""
        msg = format % args
        if "/v1/chat/completions" in msg:
            self.request_count += 1
        print(f"[proxy] {msg}")


import os

def main():
    parser = argparse.ArgumentParser(description="Free AI API Starter Kit — Local Proxy")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG), help="Path to working_endpoints.json")
    args = parser.parse_args()

    print(f"[proxy] Starting Free AI Local Proxy on port {args.port}...")
    print(f"[proxy] Config: {args.config}")

    # Load configuration
    FreeAIProxyHandler.load_config(Path(args.config))

    if not FreeAIProxyHandler.proxy_config:
        print("[proxy] No endpoints configured. Run quickstart.py first.")
        sys.exit(1)

    # Start server
    server = HTTPServer(("0.0.0.0", args.port), FreeAIProxyHandler)
    print(f"[proxy] Listening on http://localhost:{args.port}")
    print(f"[proxy] OpenAI-compatible endpoint: http://localhost:{args.port}/v1/chat/completions")
    print(f"[proxy] Models list: http://localhost:{args.port}/v1/models")
    print(f"[proxy] Health check: http://localhost:{args.port}/health")
    print("[proxy] Press Ctrl+C to stop.\n")
    print("[proxy] Ready! Point your OpenAI-compatible client at this URL.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[proxy] Shutting down...")
        server.shutdown()
        print(f"[proxy] Total requests: {FreeAIProxyHandler.request_count}")
        print(f"[proxy] Total errors: {FreeAIProxyHandler.error_count}")
        print("[proxy] Goodbye.")


if __name__ == "__main__":
    main()
