# Codebase Q&A with Proof

A monorepo app that lets you upload a ZIP of a codebase or connect a public GitHub repo, ask questions about the code, and get answers grounded in retrieved code snippets with file paths and line ranges (proof).

**Live link:** [To be filled after deployment]

## What is implemented

- **Monorepo**: `backend/` (Python + FastAPI), `frontend/` (React + Vite).
- **Indexing**: Upload ZIP of codebase or index via public GitHub repo URL.
- **Vector store**: Chroma (local only), no cloud vector DBs.
- **LLM & embeddings**: OpenAI API or OpenRouter (keys and optional base URL from environment only).
- **RAG**: Chunk code → embed → store in Chroma → retrieve top chunks for a question → LLM answers using only retrieved snippets.
- **API**: `POST /index/zip`, `POST /index/github`, `POST /qa`, `GET /health`, `POST /refactor`, `GET /history`.
- **Q&A response**: Final answer, references (file path + line ranges), and retrieved code snippets.
- **Frontend**: Home, Q&A, Status (backend/DB/LLM health), History (last 10 Q&As).
- **Error handling**: Empty upload, invalid GitHub URL, asking before indexing.
- **Last 10 Q&As** stored in memory.
- **“Make it your own”**: Refactor suggestions button with file references.
- **Docker**: Dockerfile per app + `docker-compose` to run the whole stack with one command.

## What is not implemented

- Git initialization and GitHub remote setup (you do that manually).
- User auth / multi-tenancy.
- Persistence of Q&A history across server restarts (in-memory only).
- Parsing of refactor suggestions into structured file/line fields (LLM returns a single text block).

## Architecture overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   React     │────▶│   FastAPI   │────▶│   Chroma     │
│   (Vite)    │     │   backend   │     │   (local)    │
└─────────────┘     └──────┬──────┘     └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  OpenAI API  │
                   │ (embed+LLM)  │
                   └──────────────┘
```

- **Frontend**: SPA; calls backend at `/api` (proxied in dev and in Docker via nginx).
- **Backend**: Serves index (ZIP/GitHub), Q&A, health, refactor, history. Uses Chroma for embeddings and OpenAI for embeddings + chat.
- **RAG**: Index → chunk code → embed with OpenAI → store in Chroma. Query → retrieve similar chunks → send only those to LLM → return answer + references + snippets.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Backend, vector DB, and LLM status |
| POST | `/index/zip` | Upload ZIP file; index into Chroma |
| POST | `/index/github` | Body: `{ "repo_url": "https://github.com/owner/repo" }`; clone and index |
| POST | `/qa` | Body: `{ "question": "..." }`; answer + references + retrieved_snippets |
| POST | `/refactor` | Generate refactor suggestions (with file references) from indexed code |
| GET | `/history` | Last 10 Q&A entries |

## How to run locally

### With virtual environment (backend) + npm (frontend)

1. **Backend**
   - `cd backend`
   - `python3 -m venv venv`
   - `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
   - `pip install -r requirements.txt`
   - Copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

2. **Frontend**
   - `cd frontend`
   - `npm install`
   - `npm run dev`
   - Open http://localhost:3000 (Vite proxies `/api` to backend on 8000)

3. **Status**: Open the Status page to confirm backend, Chroma, and LLM are OK. Then index a ZIP or GitHub repo on the Q&A page and ask a question.

### With Docker (one command)

1. In the repo root, copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Run: `docker compose up --build`
3. Open http://localhost:3000 (frontend). API is at http://localhost:3000/api (proxied to backend).

Backend runs on port 8000; frontend (nginx) on 3000. Chroma data is persisted in a Docker volume.

## Live hosting

After deploying (e.g. to a VPS or PaaS), set the **Live link** at the top of this README to your app URL.

### Using OpenRouter

To use an OpenRouter API key instead of OpenAI, set in `.env`:

```bash
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
```

Model names default to `openai/text-embedding-3-small` and `openai/gpt-4o-mini` when the base URL contains `openrouter`. You can override with `OPENAI_EMBEDDING_MODEL` and `OPENAI_CHAT_MODEL` if needed.