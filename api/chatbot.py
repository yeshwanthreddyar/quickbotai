
import os
import time

# Optional OpenAI integration (uses the 'openai' library if available)
USE_OPENAI = True
try:
    import openai
    from openai import OpenAI
except Exception:
    USE_OPENAI = False
    openai = None
    OpenAI = None

def _openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    # New OpenAI client style
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception:
        return None

def generate_reply(message, history=None, model="openai:gpt-4o-mini", temperature=0.7):
    """Return (reply_text, meta_dict). If no API key, uses a simple offline rule-based fallback."""
    history = history or []
    meta = {
        "provider": "offline" if not USE_OPENAI or not _openai_client() else "openai",
        "model": model,
        "temperature": temperature,
        "latency_ms": None
    }

    start = time.time()

    client = _openai_client() if USE_OPENAI else None
    if client is not None and model.startswith("openai:"):
        # Map friendly name to actual model id
        model_id = model.split("openai:", 1)[1] or "gpt-4o-mini"
        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are QuickBot AI. Be concise and helpful."},
                    *[{"role": m.get("role","user"), "content": m.get("content","")} for m in history],
                    {"role": "user", "content": message},
                ],
                temperature=temperature,
            )
            text = resp.choices[0].message.content.strip()
            meta["provider"] = "openai"
            meta["model"] = model_id
            meta["latency_ms"] = int((time.time() - start) * 1000)
            return text, meta
        except Exception as e:
            # Fall back to offline mode
            meta["provider"] = "offline_fallback"
            meta["error"] = str(e)

    # Offline simple response
    canned = _offline_reply(message)
    meta["latency_ms"] = int((time.time() - start) * 1000)
    return canned, meta

def _offline_reply(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in ["hi", "hello", "hey"]):
        return "Hey! 👋 I’m online. How can I help you today?"
    if "help" in msg:
        return "Sure — tell me what you’re trying to do, and I’ll guide you step by step."
    if "render" in msg:
        return "On Render, ensure your Start Command uses gunicorn for Flask and that your static UI is built into the web/ folder."
    return f"You said: {message}\n(Offline mode: set OPENAI_API_KEY to enable real AI replies.)"
