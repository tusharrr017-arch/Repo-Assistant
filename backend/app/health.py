"""Health: backend, Chroma, LLM."""
from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_BASE_URL
from .vector_store import VectorStore


def check_backend() -> dict:
    return {"status": "ok", "message": "Backend is running"}


def check_vector_db(vector_store: VectorStore) -> dict:
    try:
        ok = vector_store.is_available()
        count = vector_store.count() if ok else 0
        return {
            "status": "ok" if ok else "error",
            "message": "Chroma is available" if ok else "Chroma is not available",
            "chunk_count": count,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "chunk_count": 0}


def check_llm() -> dict:
    if not OPENAI_API_KEY:
        return {"status": "error", "message": "OPENAI_API_KEY is not set"}
    try:
        kwargs: dict = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            kwargs["base_url"] = OPENAI_BASE_URL.rstrip("/")
        client = OpenAI(**kwargs)
        client.models.list()
        provider = "OpenRouter" if OPENAI_BASE_URL and "openrouter" in OPENAI_BASE_URL.lower() else "OpenAI"
        return {"status": "ok", "message": f"LLM ({provider}) connection OK"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_health(vector_store: VectorStore) -> dict:
    backend = check_backend()
    db = check_vector_db(vector_store)
    llm = check_llm()
    overall = "ok" if all(x.get("status") == "ok" for x in (backend, db, llm)) else "degraded"
    return {"status": overall, "backend": backend, "vector_db": db, "llm": llm}
