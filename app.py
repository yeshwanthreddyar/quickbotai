
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
from api.chatbot import generate_reply

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(APP_DIR, "web")

app = Flask(__name__, static_folder=os.path.join(WEB_DIR, ""), static_url_path="")
CORS(app)

# --------- Static UI (React build) ---------
# Serve index.html at root
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_ui(path):
    if path and os.path.exists(os.path.join(WEB_DIR, path)):
        return send_from_directory(WEB_DIR, path)
    # default to index.html for SPA routes
    return send_from_directory(WEB_DIR, "index.html")


# --------- API ---------
@app.post("/api/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get("message", "").strip()
    history = data.get("history", [])
    model = data.get("model", "openai:gpt-4o-mini")
    temperature = float(data.get("temperature", 0.7))

    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    reply, meta = generate_reply(user_msg, history=history, model=model, temperature=temperature)
    return jsonify({
        "reply": reply,
        "meta": meta
    })


def create_app():
    return app


# For local debugging: python app.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
