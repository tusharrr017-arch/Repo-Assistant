"""RAG: retrieve chunks from Chroma, answer via LLM using only those snippets."""
import re
from typing import List, Tuple

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_CHAT_MODEL, MAX_RETRIEVAL_CHUNKS
from .vector_store import VectorStore


def _parse_cited_chunks(raw_answer: str) -> Tuple[str, List[dict]]:
    """Extract CITED: path (start-end); ... from LLM response. Returns (answer_text, refs)."""
    cited_refs: List[dict] = []
    answer = raw_answer
    match = re.search(r"\n\s*CITED:\s*(.+?)(?=\n\n|\n*$)", raw_answer, re.DOTALL | re.IGNORECASE)
    if match:
        cited_block = match.group(1).strip()
        answer = raw_answer[: match.start()].strip()
        part_re = re.compile(r"([^\n;]+?)\s*\(\s*(\d+)\s*[-–]\s*(\d+)\s*\)")
        for m in part_re.finditer(cited_block):
            path = m.group(1).strip().strip('"\'')
            cited_refs.append({
                "file_path": path,
                "start_line": int(m.group(2)),
                "end_line": int(m.group(3)),
            })
    return answer, cited_refs


def _openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    kwargs: dict = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL.rstrip("/")
    return OpenAI(**kwargs)


def _format_snippets(chunks: List[dict]) -> str:
    parts = []
    for c in chunks:
        path = c.get("file_path", "")
        start, end = c.get("start_line", 0), c.get("end_line", 0)
        parts.append(f"--- {path} (lines {start}-{end}) ---\n{c.get('text', '')}")
    return "\n\n".join(parts)


SYSTEM_PROMPT = """You are a code Q&A assistant. Answer using ONLY the provided code snippets. If the answer is not in the snippets, say "I could not find this in the provided code." Cite (file_path, lines X-Y) where relevant.

On the last line of your response write exactly:
CITED: path1 (start-end); path2 (start-end)
List only the snippets you used. Example: CITED: backend/README.md (16-50)"""


def answer_with_rag(
    vector_store: VectorStore,
    question: str,
    n_chunks: int = MAX_RETRIEVAL_CHUNKS,
) -> dict:
    results = vector_store.query(question, n_results=n_chunks)
    if not results or not results.get("documents") or not results["documents"][0]:
        return {
            "answer": "No relevant code was found. Please index a codebase first and ensure your question relates to the code.",
            "references": [],
            "retrieved_snippets": [],
        }

    docs = results["documents"][0]
    meta_list = results.get("metadatas") and results["metadatas"][0] or [{}] * len(docs)

    references = []
    retrieved_snippets = []
    for text, meta in zip(docs, meta_list):
        path = meta.get("file_path", "")
        start = int(meta.get("start_line", 0))
        end = int(meta.get("end_line", 0))
        references.append({"file_path": path, "start_line": start, "end_line": end})
        retrieved_snippets.append({"file_path": path, "start_line": start, "end_line": end, "text": text})

    snippets_block = _format_snippets(retrieved_snippets)
    user_content = f"Code snippets:\n\n{snippets_block}\n\nQuestion: {question}\n\nAnswer using only the above snippets. At the end add: CITED: <path (start-end) for each snippet you used>."

    try:
        resp = _openai_client().chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        raw_answer = resp.choices[0].message.content or ""
        answer, cited_refs = _parse_cited_chunks(raw_answer)
        if cited_refs:
            references = cited_refs
    except Exception as e:
        answer = f"LLM error: {str(e)}"

    return {"answer": answer, "references": references, "retrieved_snippets": retrieved_snippets}


REFACTOR_SYSTEM_PROMPT = """You are a refactoring assistant. Using ONLY the provided code snippets, suggest concrete refactors (extract function, rename, simplify). For each: short title, file path and line range, brief description. Be concise."""


def refactor_suggestions(vector_store: VectorStore, n_chunks: int = 15) -> dict:
    results = vector_store.query("code structure functions classes", n_results=n_chunks)
    if not results or not results.get("documents") or not results["documents"][0]:
        return {"suggestions": [], "retrieved_snippets": [], "message": "No code indexed. Index a codebase first."}

    docs = results["documents"][0]
    meta_list = results.get("metadatas", [[]])[0] or [{}] * len(docs)
    retrieved_snippets = []
    for meta, text in zip(meta_list, docs):
        retrieved_snippets.append({
            "file_path": meta.get("file_path", ""),
            "start_line": int(meta.get("start_line", 0)),
            "end_line": int(meta.get("end_line", 0)),
            "text": text,
        })
    snippets_block = _format_snippets(retrieved_snippets)
    user_content = f"Code snippets:\n\n{snippets_block}\n\nSuggest 3-5 refactoring improvements with file path and line ranges for each."

    try:
        resp = _openai_client().chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": REFACTOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
        )
        raw = resp.choices[0].message.content or ""
        suggestions = [{"title": "Refactor suggestions", "description": raw, "file_path": "", "start_line": 0, "end_line": 0}]
    except Exception as e:
        suggestions = [{"title": "Error", "description": str(e), "file_path": "", "start_line": 0, "end_line": 0}]

    return {"suggestions": suggestions, "retrieved_snippets": retrieved_snippets, "message": ""}
