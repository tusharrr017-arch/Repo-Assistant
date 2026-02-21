## AI Usage Notes

AI (via Cursor) was used for:

1. Initial project bootstrap and monorepo scaffolding (backend + frontend).
2. OpenAI and OpenRouter integration (env-based: OPENAI_API_KEY, optional OPENAI_BASE_URL).
3. Initial UI components and layouts.
4. Bug fixes, refactors, and iteration.
5. Code review and formatting suggestions.

Manually verified:

- End-to-end RAG: chunk → embed → Chroma → retrieve → LLM answer grounded in snippets.
- Chroma only (no Pinecone, Weaviate, Supabase); file path and line range metadata.
- API contracts, error handling (invalid GitHub URL, empty ZIP, Q&A before indexing).
- Health endpoint: backend, vector DB, LLM status.
- No API keys in code; config from env; .gitignore for .env, venv, chroma_data.
- Code cleaned of AI noise; structure and readability checked.

LLM and embeddings:

- **Provider:** OpenAI or OpenRouter. Set `OPENAI_API_KEY`; for OpenRouter also set `OPENAI_BASE_URL=https://openrouter.ai/api/v1`.
- **Embeddings:** OpenAI-compatible API (OpenAI or OpenRouter) via same env.
- **Rationale:** Single env-based config supports both direct OpenAI and OpenRouter for model flexibility.