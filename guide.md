# Free AI API Guide (2026 Edition)

## The Complete Reference for Free AI Access

This is the comprehensive guide included in the **Free AI API Starter Kit**.
It covers every free AI API endpoint we know of, with working examples.

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Getting Free API Keys](#getting-free-api-keys)
3. [OpenRouter Free](#openrouter-free)
4. [Hugging Face Inference](#hugging-face-inference)
5. [Google Gemini Free Tier](#google-gemini-free-tier)
6. [Groq Free Tier](#groq-free-tier)
7. [Cerebras Free Tier](#cerebras-free-tier)
8. [SambaNova Free Tier](#sambanova-free-tier)
9. [Cloudflare Workers AI](#cloudflare-workers-ai)
10. [Other Free Providers](#other-free-providers)
11. [Using with OpenAI-Compatible Tools](#using-with-openai-compatible-tools)
12. [Best Practices and Gotchas](#best-practices-and-gotchas)

---

## The Big Picture

As of late 2026, AI API providers offer surprisingly generous free tiers.
These are not "trial" credits that expire in 7 days — many of them are
permanently free, with usage-based rate limits.

### What "Free" Actually Means

| Type | Example | Renewal | What You Need |
|------|---------|---------|---------------|
| Free tier (permanent) | Groq, Cerebras, Gemini | Daily/Monthly quota | Email only |
| Free credits | OpenRouter ($1 credit) | One-time, but refreshes with activity | Email + account |
| Free tier (rate-limited) | HF Inference, Cloudflare | Per minute/hour | Email + account |
| Community free | Various | Varies | Depends |

**Key insight**: You can combine multiple free tiers into a single "free AI"
setup that covers most use cases without ever paying.

### The Ideal Setup

- **Groq** for speed (2-3s responses)
- **Gemini** for large context (1M tokens free)
- **OpenRouter** for variety (50+ free models)
- **HF** for specific models not on other platforms

---

## Getting Free API Keys

All providers below require email + account, but **none require a credit card**.

| Provider | Sign-up URL | What you need |
|----------|-------------|---------------|
| OpenRouter | https://openrouter.ai | Email + password |
| Hugging Face | https://huggingface.co | Email + password |
| Google AI Studio | https://aistudio.google | Google account |
| Groq | https://console.groq.com | Email + password |
| Cerebras | https://inference.cerebras.ai | Email + password |
| SambaNova | https://cloud.sambanova.ai | Email + password |
| Cloudflare | https://dash.cloudflare.com | Cloudflare account |

### Security tip

Never put API keys in source code. Store them in environment variables:

```bash
export OPENROUTER_API_KEY="sk-or-..."
export HF_API_KEY="hf-..."
# etc.
```

Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
```

---

## OpenRouter Free

**Free models**: 50+ models, $0 credit needed
**Rate limit**: Per-model limits, generally generous
**Sign-up**: https://openrouter.ai

### Available free models (2026)

- `meta-llama/llama-3.1-8b-instruct` — fast, general purpose
- `google/gemini-flash-1.5` — long context, large input
- `mistralai/mistral-7b-instruct` — compact, capable
- `microsoft/phi-3-mini` — fast, efficient
- `deepseek/deepseek-chat` — strong reasoning
- `qwen/qwen2.5-72b-instruct` — multilingual

### Installation

```bash
pip install openai
```

### Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-...",
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="meta-llama/llama-3.1-8b-instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Tips

- Use `/api/v1/models` to see all available models
- Add `HTTP-Referer` header to get better rate limits:
  ```python
  headers = {"HTTP-Referer": "https://myapp.dev"}
  ```

---

## Hugging Face Inference

**Free models**: Any model on HF with "Inference" enabled
**Rate limit**: 6000 calls/min for free models, varies by model
**Sign-up**: https://huggingface.co/settings/tokens

### Getting your key

1. Sign up at huggingface.co
2. Go to Settings → Access Tokens
3. Create a "Read" token
4. Use it as your API key

### Usage

```python
import requests

url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
headers = {"Authorization": "Bearer hf-..."}

response = requests.post(url, headers=headers, json={"inputs": "Hello!"})
print(response.json())
```

### Target models

- `Qwen/Qwen2.5-7B-Instruct` — strong multilingual
- `mistralai/Mistral-7B-Instruct-v0.3` — well-rounded
- `meta-llama/Llama-3.1-8B-Instruct` — solid general model

### Gotchas

- Models may be "cold" (first request takes 10-30s to load)
- Shared GPU: your request may queue behind others
- Not all models are optimized for HF Inference

---

## Google Gemini Free Tier

**Free models**: gemini-2.0-flash-lite, gemini-2.0-flash, gemini-2.5-flash
**Rate limit**: 15 requests/minute free
**Sign-up**: https://aistudio.google/app/apikey

### Getting your key

1. Go to https://aistudio.google/app/apikey
2. Click "Create API Key"
3. Copy the key

### Usage (Python)

```python
import requests

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIza..."
headers = {"Content-Type": "application/json"}
body = {
    "contents": [{"parts": [{"text": "Hello!"}]}],
    "generationConfig": {"maxOutputTokens": 1000}
}

response = requests.post(url, headers=headers, json=body)
result = response.json()
print(result["candidates"][0]["content"]["parts"][0]["text"])
```

### Tips

- **1M token context**: Gemini 2.0 supports a 1 million token context free
- **Multimodal**: Can take text, images, and PDFs as input
- **Grounding**: Free grounding with Google Search

---

## Groq Free Tier

**Free models**: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
**Rate limit**: 14,400 tokens/minute free
**Sign-up**: https://console.groq.com/keys

### Key advantage: **Speed**

Groq's custom LPU architecture delivers sub-second inference for small models,
and 1-2 second responses for 70B models. If you need speed, Groq wins.

### Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="gsk-...",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Explain quantum computing in one paragraph."}]
)
print(response.choices[0].message.content)
```

### Available models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| llama-3.3-70b-versatile | 70B | ~1s | Complex reasoning |
| llama-3.1-8b-instant | 8B | ~0.3s | Simple tasks, chat |
| llama-3.1-70b-versatile | 70B | ~1s | Balanced |
| mixtral-8x7b-32768 | 47B | ~1.5s | Multilingual |
| gemma2-9b-it | 9B | ~0.5s | Lightweight |

---

## Cerebras Free Tier

**Free models**: llama-3.1-8b
**Rate limit**: 30,000 tokens/day free
**Sign-up**: https://inference.cerebras.ai/api-key

### Why Cerebras

- **Extremely fast**: Custom silicon, 50x faster than GPUs
- **Long context**: 128K context for free
- **Simple API**: OpenAI-compatible

### Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="csk-...",
    base_url="https://api.cerebras.ai/v1"
)

response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Gotcha

30K tokens/day = ~15-20 paragraph-length prompts. Use as a backup, not primary.

---

## SambaNova Free Tier

**Free models**: Meta-Llama-3.3-70B-Instruct, Llama-3.1-8B-Instruct
**Rate limit**: Community pool (varies)
**Sign-up**: https://cloud.sambanova.ai/apis

### Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-key",
    base_url="https://api.sambanova.ai/v1"
)

response = client.chat.completions.create(
    model="Meta-Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Status

⚠️ SambaNova's free tier has been less stable in 2025-2026. Sign up early
to lock in your account, but don't rely on it as your only provider.

---

## Cloudflare Workers AI

**Free models**: llama-2.1-7b-chat, llama-3-8b-instruct, mistral-7b
**Rate limit**: 10,000 neurons/day per model
**Sign-up**: https://dash.cloudflare.com

### Why Cloudflare

- **Edge network**: Low latency worldwide
- **Free forever**: Not a trial
- **Works with Workers**: Deploy AI at the edge

### Deployment

1. Sign up at cloudflare.com
2. Create a Worker
3. Use the AI binding:

```javascript
// worker.js
export default {
  async fetch(request, env) {
    const response = await env.AI.run(
      "@cf/meta/llama-3-8b-instruct-bf16",
      { messages: [{ role: "user", content: "Hello!" }] }
    );
    return new Response(JSON.stringify(response), {
      headers: { "Content-Type": "application/json" }
    });
  }
};
```

### Limitation

10K neurons ≈ ~100-200 requests/day. Great for prototypes, not for production.

---

## Other Free Providers

### GigaGPU
- **URL**: https://cloud.gigagpu.com
- **Free tier**: Limited daily requests
- **Models**: mixtral-8x7b, llama-3.1-8b, phi-3
- **Status**: May have queue/availability issues

### Predibase
- **URL**: https://predibase.com
- **Free tier**: Free GPU hours
- **Models**: llama-2-13b-chat, custom LoRA models
- **Best for**: Trying LoRA/fine-tuned models without hosting GPUs

### OctoAI
- **URL**: https://app.octoai.com
- **Free tier**: Credit hours
- **Models**: llama-3.1-8b, mixtral-8x7b
- **Status**: Varies, try it out

---

## Using with OpenAI-Compatible Tools

The beauty of modern AI: most providers speak the OpenAI API format.
This means you can point any OpenAI-compatible tool at any provider.

### Tools that work

| Tool | How to configure |
|------|-----------------|
| **Cursor** (code editor) | Settings → OpenAI API → Custom base URL |
| **Continue** (IDE extension) | Config → openai.baseURL |
| **Dify** (LLM app platform) | Model → Custom OpenAI API |
| **OpenCode** | `"baseURL": "http://localhost:8080/v1"` |
| **AutoGPT** | Custom OpenAI API URL |
| **PrivateGPT** | `.env` → `OPENAI_API_BASE_URL` |
| **Text Generation Web UI** | Settings → OpenAI API Settings |
| **LobeChat** | Settings → Model provider → OpenAI compatible |

### Example: Cursor with Groq (free)

1. Get your free Groq key from console.groq.com/keys
2. Cursor → Settings (Ctrl+,) → OpenAI API
3. Enable "Custom OpenAI API"
4. Base URL: `https://api.groq.com/openai/v1`
5. API Key: `gsk-...`

### Example: Local proxy setup (included in kit)

```bash
# Start the local proxy from the kit
python3 local_proxy.py --port 8080

# Or use with the included quickstart
python3 quickstart.py

# Point any tool at http://localhost:8080/v1
```

---

## Best Practices and Gotchas

### 1. Always have a backup provider

Free tiers change. Rate limits get tighter. Models get deprecated.
Always configure a primary + backup + tertiary.

```python
providers = [
    ("groq", "https://api.groq.com/openai/v1"),
    ("openrouter", "https://openrouter.ai/api/v1"),
    ("cerebras", "https://api.cerebras.ai/v1"),
]
# Try in order, fall back on failure
```

### 2. Monitor your usage

Most free tiers have per-minute AND per-day limits. Hit a minute limit
and your request fails. Hit a day limit and you're blocked for 24h.

### 3. Small models are fine for most tasks

You'd be surprised how good an 8B model is with a good system prompt.
Don't default to 70B — reserve it for complex reasoning.

### 4. Cache everything

If you're calling the API with similar inputs, cache the results:

```python
import hashlib
import json
import os

def cache_key(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()[:32]

def call_with_cache(prompt, call_fn):
    k = cache_key(prompt)
    path = f"/tmp/ai_cache_{k}.json"
    if os.path.exists(path):
        return json.load(open(path))
    result = call_fn(prompt)
    json.dump({"input": prompt, "output": result}, open(path, "w"))
    return result
```

### 5. Set conservative temperature

For production use, `temperature=0.3` gives more consistent results.
For creative work, `0.7-0.9` is fine.

### 6. Beware of context limits

Check the model's context window. Sending a 100K-token prompt to a
4K-context model wastes your rate limit on an error.

### 7. Use streaming

```
```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    stream=True  # Streams tokens instead of blocking
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

### 8. Security

- Never hardcode API keys
- Rotate keys if you suspect leakage
- Rate-limit your own API calls to avoid hitting provider limits
- Never send sensitive data (passwords, keys, personal info) to external APIs

### 9. Cost tracking

Even though everything is free, read the fine print:
- Some providers have a "free credit" AND a paid tier
- Some free tiers require a card on file (for abuse prevention)
- Some "free" tiers expire after N days

### 10. Report outages

If a provider goes down or a model disappears, the kit includes a
check script:

```bash
python3 check_endpoints.py
```

This re-tests all endpoints and updates your configuration.

---

## Summary: Your Free AI Stack

| Role | Primary | Backup | Why |
|------|---------|--------|-----|
| Speed | Groq | Cerebras | Lord of fast inference |
| Long Context | Gemini | OpenRouter | 1M tokens free |
| Variety | OpenRouter | HF Inference | 50+ free models |
| Local/Edge | Cloudflare | — | Edge deployment free |
| Backup | Cerebras | SambaNova | When others are down |

**Total monthly cost: $0.**

---

## Legal and Terms

Each provider's terms allow personal/commercial use of their free tier,
but check the specific terms when you sign up. Key points:

1. **Rate limits** apply per account, not per API key
2. **Self-serving** (automated bulk requests) may violate terms
3. **Data retention** varies — some providers use your data for training
4. **Content ownership** — typically you own your inputs, not generated outputs
5. **Output usage** — most allow commercial use of outputs with attribution

When in doubt, check the provider's terms page before deploying commercially.

---

*Last updated: 2026-11-05. This guide is part of the Free AI API Starter Kit.*
