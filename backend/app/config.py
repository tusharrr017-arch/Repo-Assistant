"""Env-based configuration. No secrets in code."""
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

if OPENAI_BASE_URL and "openrouter" in OPENAI_BASE_URL.lower():
    _default_embedding, _default_chat = "openai/text-embedding-3-small", "openai/gpt-4o-mini"
else:
    _default_embedding, _default_chat = "text-embedding-3-small", "gpt-4o-mini"

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", _default_embedding)
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", _default_chat)

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "codebase_qa")

MAX_QA_HISTORY = 10
MAX_RETRIEVAL_CHUNKS = 6
