# Tutorly

Tutorly is a local AI-powered learning app with a Flask API, SQLite storage, Gemini-backed chat, and a Vite + React frontend.

## Project Structure

```text
.
|-- app.py                 # Flask app, API routes, SQLite setup, Gemini service
|-- run_server.py          # Local server bootstrap and environment loading
|-- requirements.txt       # Python dependencies
|-- package.json           # Node/Vite scripts and frontend dependencies
|-- index.html             # Vite development HTML entry
|-- src/                   # React source code
|-- static/                # Flask-served production frontend and stable assets
|-- uploads/               # Runtime upload placeholder, ignored except .gitkeep
`-- docs/                  # Project structure and architecture notes
```

Runtime files such as `.env`, `.venv/`, `node_modules/`, logs, `tutorly.db`, and generated Python caches are intentionally ignored.

## Setup

```powershell
npm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `GEMINI_API_KEY` in `.env` before using AI chat.

## Development

Run the API:

```powershell
npm run dev:api
```

Run the Vite frontend in another terminal:

```powershell
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the Flask API on `http://localhost:5000`.

## Production Build

```powershell
npm run build
npm run serve
```

The production frontend is built into `static/` so Flask can serve it at `/static/`.

## Validation

```powershell
npm run build
python -m py_compile app.py run_server.py
```
