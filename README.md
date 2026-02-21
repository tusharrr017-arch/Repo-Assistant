# Codebase Q&A with Proof

Ask questions about your codebase and get answers grounded in retrieved code, with **file and line references**. Index via **ZIP upload** or **public GitHub repo URL**, then ask questions or generate refactor suggestions.

## Features

- **Index codebase** — Upload a ZIP of your repo or paste a public GitHub URL; the backend extracts code, chunks it, and embeds it in a vector store (ChromaDB).
- **Q&A** — Ask natural-language questions; answers cite specific files and line ranges with snippets.
- **Refactor suggestions** — Generate improvement ideas with file references from the indexed code.
- **History** — Recent Q&A entries and indexing events.
- **Status** — Health check and index stats (backend + embeddings).

---

## Try it live (Render)

| Link | Description |
|------|-------------|
| [**Frontend**](https://repo-assistant-frontend.onrender.com/) | Use the app in the browser |
| [**Backend**](https://repo-assistant-backend.onrender.com) | API root; interactive docs at [Backend `/docs`](https://repo-assistant-backend.onrender.com/docs) |

**Notes for the live demo:**

- **Use small ZIPs only** — The app runs on Render’s free tier (512 MB RAM). Large uploads may time out or fail. Prefer small repos or a subset of files.
- **If upload fails or you see “failed to fetch”** — Use **“Or GitHub repo URL”** instead: paste a **public** GitHub repo URL (e.g. `https://github.com/owner/repo`) and click **Index from GitHub**. The backend will clone and index the repo.

---

## Project structure

```
├── backend/          # FastAPI app, ChromaDB, OpenAI/OpenRouter
│   ├── app/
│   │   ├── api.py    # Routes: index/zip, index/github, qa, health, history
│   │   ├── config.py # Env-based config
│   │   ├── vector_store.py
│   │   ├── zip_loader.py
│   │   ├── github_loader.py
│   │   └── ...
│   ├── .env.example
│   └── requirements.txt
├── frontend/         # React + Vite + TypeScript
│   ├── src/
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Local development

### Prerequisites

- **Docker** (recommended), or **Python 3.11+** and **Node.js** for running backend and frontend separately.
- An **OpenAI** or **OpenRouter** API key for embeddings and chat.

### Quick start (Docker)

1. Copy `backend/.env.example` to `backend/.env` and set your API key:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env: OPENAI_API_KEY=sk-...
   ```
2. From the project root:
   ```bash
   docker compose up --build
   ```
3. Open [http://localhost:3000](http://localhost:3000). The frontend proxies `/api` to the backend at port 8000.

### Without Docker

- **Backend:**  
  `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
- **Frontend:**  
  `cd frontend && npm install && npm run dev`  
  (Ensure the frontend is configured to talk to `http://localhost:8000` for API requests, e.g. via proxy or `VITE_API_URL`.)
- Set `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL` for OpenRouter) in `backend/.env` or your environment.

### Environment variables (backend)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI or OpenRouter API key. |
| `OPENAI_BASE_URL` | No | Override API base (e.g. `https://openrouter.ai/api/v1` for OpenRouter). |
| `OPENAI_EMBEDDING_MODEL` | No | Default: `text-embedding-3-small` (or `openai/text-embedding-3-small` for OpenRouter). |
| `OPENAI_CHAT_MODEL` | No | Default: `gpt-4o-mini` (or `openai/gpt-4o-mini` for OpenRouter). |
| `CHROMA_PERSIST_DIR` | No | Directory for ChromaDB data (default: `./chroma_data`). |
| `CHROMA_COLLECTION_NAME` | No | Collection name (default: `codebase_qa`). |

Copy `backend/.env.example` to `backend/.env` and fill in; do not commit `.env` or API keys.

### Using OpenRouter

In `backend/.env`:

```env
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
```

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/index/zip` | Index code from an uploaded ZIP file (multipart). |
| POST | `/index/github` | Index code from a public GitHub repo URL (JSON body: `repo_url`). |
| POST | `/qa` | Ask a question (JSON: `question`); returns answer and sources. |
| GET | `/health` | Backend and embedding service status. |
| GET | `/history` | Recent Q&A and indexing history. |

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs) when running locally, or [Backend `/docs`](https://repo-assistant-backend.onrender.com/docs) for the live backend.

---

## Deploying to Render (or similar)

- **Backend:** Build from `backend/` (or repo root with build context `backend/`). Set env vars (e.g. `OPENAI_API_KEY`, optional `OPENAI_BASE_URL`). Use a persistent disk if you want ChromaDB data to survive restarts (Render: attach a disk to the backend service).
- **Frontend:** Build from `frontend/` (e.g. `npm run build`); set `VITE_API_URL` (or equivalent) to your backend URL so the built app calls the correct API. Serve the `dist/` output with a static host or nginx.
- **Free tier:** 512 MB RAM — keep ZIP uploads small; prefer GitHub URL for larger repos.

---

## Tech stack

- **Backend:** FastAPI, ChromaDB, OpenAI-compatible embeddings and chat (OpenAI or OpenRouter).
- **Frontend:** React, Vite, TypeScript, React Router, react-markdown, react-syntax-highlighter.

---

## Troubleshooting

- **“OPENAI_API_KEY environment variable is not set”** — Create `backend/.env` from `backend/.env.example` and set `OPENAI_API_KEY`. With Docker, ensure the backend service uses `env_file: backend/.env` (or equivalent) so the container sees the key.
- **“API key is invalid or was rejected”** — Use a valid key from [OpenAI](https://platform.openai.com/account/api-keys) or [OpenRouter](https://openrouter.ai/keys). For OpenRouter, set `OPENAI_BASE_URL=https://openrouter.ai/api/v1`.
- **“No embedding data received” / indexing fails on large ZIP** — Backend batches adds and skips empty chunks; if it still fails, try a smaller ZIP or index via GitHub URL instead.
- **“Failed to fetch” in browser** — Backend may be down or CORS/URL wrong. For the live demo, try **Index from GitHub** with a public repo URL.

---

## License

MIT (or as specified in the repo).
