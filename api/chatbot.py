import os
import time

# --- Gemini Integration ---
USE_GEMINI = True
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    USE_GEMINI = False
    genai = None

# --- Optional OpenAI fallback (if needed) ---
USE_OPENAI = True
try:
    import openai
    from openai import OpenAI
except Exception:
    USE_OPENAI = False
    openai = None
    OpenAI = None


def _gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not USE_GEMINI:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai
    except Exception:
        return None


def _openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not USE_OPENAI:
        return None
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception:
        return None


def generate_reply(message, history=None, model="gemini-1.5-flash", temperature=0.7):
    """
    Return (reply_text, meta_dict).
    If Gemini or OpenAI API key is missing, uses simple offline fallback.
    """
    history = history or []
    meta = {
        "provider": "offline",
        "model": model,
        "temperature": temperature,
        "latency_ms": None
    }

    start = time.time()

    # --- Try Gemini first ---
    client = _gemini_client()
    if client is not None:
        try:
            model_id = model or "gemini-2.5-flash"
            model_obj = client.GenerativeModel(model_id)

            # Build full conversation context
            prompt = (
                "You are QuickBot AI. Be concise and helpful.\n\n" +
                "\n".join([f"{m.get('role','user')}: {m.get('content','')}" for m in history]) +
                f"\nuser: {message}"
            )

            resp = model_obj.generate_content(prompt)
            text = resp.text.strip()
            meta["provider"] = "gemini"
            meta["model"] = model_id
            meta["latency_ms"] = int((time.time() - start) * 1000)
            return text, meta
        except Exception as e:
            meta["provider"] = "gemini_fallback"
            meta["error"] = str(e)

    # --- Try OpenAI (optional) ---
    client = _openai_client()
    if client is not None and model.startswith("openai:"):
        try:
            model_id = model.split("openai:", 1)[1] or "gpt-4o-mini"
            resp = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are QuickBot AI. Be concise and helpful."},
                    *[{"role": m.get("role", "user"), "content": m.get("content", "")} for m in history],
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
            meta["provider"] = "openai_fallback"
            meta["error"] = str(e)

    # --- Offline fallback ---
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
    return f"You said: {message}\n(Offline mode: set GEMINI_API_KEY to enable real AI replies.)"
