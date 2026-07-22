"""
Optional LLM client — used only to polish the recommendation prose.

Tries a free Groq endpoint (if GROQ_API_KEY is set), then a local Ollama server
(if running), otherwise returns None so the caller uses its deterministic template.
No paid dependency is required for the system to work.
"""
import os

try:
    import requests
except Exception:  # requests not installed
    requests = None

SYSTEM = "You are an industrial EV battery maintenance assistant. Be concise and factual; never invent data."


def generate(prompt: str, system: str = SYSTEM):
    if requests is None:
        return None

    # 1) Groq (free tier), OpenAI-compatible
    key = os.getenv("GROQ_API_KEY")
    if key:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 300,
                },
                timeout=30,
            )
            if r.ok:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    # 2) Local Ollama
    base = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        r = requests.post(
            f"{base}/api/generate",
            json={"model": os.getenv("OLLAMA_MODEL", "llama3.1"),
                  "prompt": f"{system}\n\n{prompt}", "stream": False},
            timeout=30,
        )
        if r.ok:
            return (r.json().get("response") or "").strip() or None
    except Exception:
        pass

    return None
