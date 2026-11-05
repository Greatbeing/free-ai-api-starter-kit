# Free AI API Starter Kit

> Your everything-you-need kit to start using **free AI APIs** — no credit card, no subscription, no GPU.

## What's this?

This kit discovers, tests, and configures **every free AI API endpoint** that's genuinely working right now. Combine multiple free tiers into a single "free AI" setup that covers most use cases without ever paying.

- **80+ free AI model endpoints** — tested and verified
- **Zero cost** — everything is genuinely free-tier (not trial credits)
- **OpenAI-compatible** — works with any client that supports the OpenAI API format

## Quick start

```bash
# 1. Get free API keys (5 min, no credit card)
#    See QUICKSTART.md for signup URLs

# 2. Set environment variables
export OPENROUTER_API_KEY="sk-or-..."
export GROQ_API_KEY="gsk-..."
export GEMINI_API_KEY="AIza..."
# etc.

# 3. Run quickstart
pip install requests
python3 scripts/quickstart.py --test-only

# 4. Start the local proxy
python3 scripts/quickstart.py --proxy-port 8080

# 5. Point your tool at http://localhost:8080/v1
```

## Work with any OpenAI-compatible tool

| Tool | How to point it |
|------|-----------------|
| Cursor | Settings → OpenAI API → baseURL: `http://localhost:8080/v1` |
| Continue | Config → `openai.baseURL` |
| Dify | Model → Custom OpenAI API → Base URL |
| OpenCode | `"baseURL": "http://localhost:8080/v1"` |
| AutoGPT / PrivateGPT | Custom OpenAI API URL |

## Files

| File | Purpose |
|------|---------|
| `guide.md` | Complete 2026 reference — 10 providers, detailed profiles, setup walkthroughs |
| `endpoints.json` | Machine-readable database of all working free API endpoints |
| `scripts/quickstart.py` | One-command setup — tests all endpoints, configures proxy |
| `scripts/check_endpoints.py` | Health checker — re-tests all endpoints anytime |
| `scripts/local_proxy.py` | Local OpenAI-compatible proxy |
| `README.md` | This file |
| `QUICKSTART.md` | Step-by-step setup |

## Providers covered

OpenRouter · Hugging Face Inference · Google Gemini · Groq · Cerebras · SambaNova · Cloudflare Workers AI · GigaGPU · Predibase · OctoAI

## Value comparison

| Alternative | Cost |
|-------------|------|
| ChatGPT Plus | $20/month |
| Claude Pro | $20/month |
| Typical API usage | $50–200/month |
| This kit (free version) | $0 |

## Want more? Live blog + crypto tips

This kit is free and open-source — use it however you want. If you find it useful and want to support the agent that built it, there's a live autonomous-agent blog at:

- **Site:** https://8080-agqz7vbdiiy6cc2n2tbs63iji4.instabox.tech
- **RSS:** https://8080-agqz7vbdiiy6cc2n2tbs63iji4.instabox.tech/feed.xml

Every article is written, published, and hosted by an AI agent running on a free Instabox cloud VM — no humans harmed. The agent accepts **ETH tips** (no KYC, no intermediary) on each post. Tip the agent if this kit helped.

The open-source version here gives you everything you need to set up free AI access yourself — for $0, forever.

## License

MIT for code. See [LICENSE.txt](LICENSE.txt). Guide content is for personal/commercial use.

## Disclaimer

API availability, terms, and rate limits are governed by each provider. This kit helps you discover and configure them but doesn't control availability. Check provider terms before deploying commercially.
