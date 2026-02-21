# Prompts used to develop this app

This file records the **prompts** used to build the Codebase Q&A with Proof app. It does **not** include API keys, model responses, or any secrets.

---

## Main project prompt (summary)

The project was built from a single detailed specification that requested:

- A production-ready monorepo for “Codebase Q&A with Proof”.
- Backend: Python + FastAPI; frontend: React (or Next.js) with a simple, clean UI.
- Vector DB: Chroma only (local).
- LLM + embeddings: OpenAI API via environment variables.
- Support for both: upload ZIP of codebase and connect via public GitHub repo URL.
- Full RAG: chunk code, embed, store in Chroma, retrieve for questions, LLM answers using only retrieved snippets.
- API: `POST /index/zip`, `POST /index/github`, `POST /qa`, `GET /health`; Q&A response must include final answer, references (file path + line ranges), and retrieved snippets.
- Frontend: Home, Q&A, Status (backend/DB/LLM health), History (last 10 Q&As).
- Error handling: empty upload, invalid GitHub URL, questions before indexing.
- Save last 10 Q&As (in memory or SQLite).
- One “Make it your own” feature: button to generate refactor suggestions with file references.
- Root docs: README.md, AI_NOTES.md, ABOUTME.md, PROMPTS_USED.md.
- .gitignore, .env.example, backend venv instructions and requirements, Dockerfile + docker-compose for one-command run.
- Constraints: no API keys in code, no external vector DBs, Chroma only; no git init or GitHub push (user does that manually).

The prompt also specified the exact folder layout for `backend/app/` (main.py, api.py, rag.py, vector_store.py, github_loader.py, zip_loader.py, health.py) and frontend pages (Home, Q&A, Status, History).

---

## Follow-up / refinement

- “Finish everything except GitHub setup. Do NOT initialize git or push to GitHub.”
- “Generate all files with working code; ensure backend runs with uvicorn; frontend can call backend APIs; health endpoint works; RAG flow works end-to-end; Docker runs with one command.”
- “Start by scaffolding the full monorepo structure and then fill in each file with correct, working code.”

---

*No API keys or model outputs are stored in this file.*
