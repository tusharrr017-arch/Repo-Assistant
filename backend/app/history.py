"""In-memory last N Q&A entries."""
from collections import deque

from .config import MAX_QA_HISTORY

_qa_history: deque = deque(maxlen=MAX_QA_HISTORY)


def add_qa(question: str, answer: str, references: list, retrieved_snippets: list) -> None:
    _qa_history.append({
        "question": question,
        "answer": answer,
        "references": references,
        "retrieved_snippets": retrieved_snippets,
    })


def get_qa_history() -> list:
    return list(_qa_history)
