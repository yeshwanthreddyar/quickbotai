
# QuickBot AI — Flask Version (Python backend + same UI)

This repo serves your existing React/Vite UI **as static files** from Flask and exposes a chat API.

## Structure
```
.
├── app.py                 # Flask server (serves UI + API)
├── api/
│   └── chatbot.py         # Chat logic (OpenAI or offline fallback)
├── web/                   # Put the built React app here (index.html + assets)
├── scripts/
│   └── copy_dist.py       # Helper to copy frontend 'dist/' into ./web/
├── requirements.txt
├── render.yaml            # Render config (Python)
├── Procfile               # Optional for local Heroku-style runs
└── .env.example
```

## How to keep the **same UI**
1) In your original React/Vite project (the one with `vite.config.ts`), build it locally:
- with Bun:
```
bun install
bun run build
```
- or with npm:
```
npm install
npm run build
```

This creates a `dist/` folder.

2) Copy the contents of `dist/` into this repo’s `web/` folder.
   You can use the helper script:
```
python scripts/copy_dist.py /path/to/your/frontend/dist ./web
```

3) Start Flask locally to verify:
```
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

4) Test the chat API:
```
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello!\"}"
```

## Deploy on Render (Python)
- Connect this repo to a **Web Service**.
- It will use `render.yaml` settings:
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn app:app`

### Environment Variables
- `OPENAI_API_KEY` (optional): set it to enable real AI responses. Without it, the bot uses a friendly offline fallback.

## Notes
- You do **not** need Node/Bun on Render. The **built** UI must exist in `./web/` at deploy time.
- If your React app uses a different base path, ensure Vite is built with `base: "/"` (default).
