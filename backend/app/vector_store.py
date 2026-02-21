"""Chroma vector store for code embeddings (OpenAI or OpenRouter via env)."""
import os
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_EMBEDDING_MODEL,
)


def _embedding_function():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    kwargs = {"api_key": OPENAI_API_KEY, "model_name": OPENAI_EMBEDDING_MODEL}
    if OPENAI_BASE_URL:
        kwargs["api_base"] = OPENAI_BASE_URL.rstrip("/")
    return embedding_functions.OpenAIEmbeddingFunction(**kwargs)


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or CHROMA_PERSIST_DIR
        os.makedirs(self.persist_directory, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = None
        self._ef = None

    def _get_collection(self):
        if self._collection is None:
            self._ef = _embedding_function()
            self._collection = self._client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                embedding_function=self._ef,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[dict]) -> None:
        self._get_collection().add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, n_results: int = 10) -> dict:
        return self._get_collection().query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    def clear(self) -> None:
        try:
            self._client.delete_collection(CHROMA_COLLECTION_NAME)
        except Exception:
            pass
        self._collection = None
        self._ef = None

    def count(self) -> int:
        try:
            return self._get_collection().count()
        except (ValueError, Exception):
            return 0

    def is_available(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False
