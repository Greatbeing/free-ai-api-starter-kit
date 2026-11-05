# Quick Start

```bash
# 1. Install Python (3.9+)
sudo apt install python3 python3-pip   # Linux
# brew install python                    # Mac

# 2. Install dependencies
pip install requests

# 3. Run the setup script
python3 quickstart.py

# 4. Start your local AI proxy (optional)
python3 local_proxy.py --port 8080
```

The proxy speaks the OpenAI API format. Point any OpenAI-compatible client at `http://localhost:8080/v1`.

## Check endpoints anytime

```bash
python3 check_endpoints.py
```

## Use with popular tools

| Tool | How to point it |
| --- | --- |
| Cursor | Settings → OpenAI API → baseURL: `http://localhost:8080/v1` |
| Continue | Config → openai.baseURL: `http://localhost:8080/v1` |
| Dify | Model → Custom OpenAI API → Base URL |
| OpenCode | `"baseURL": "http://localhost:8080/v1"` |
