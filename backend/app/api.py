"""Routes: index (zip/github), qa, health, refactor, history."""
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from openai import AuthenticationError as OpenAIAuthError
from pydantic import BaseModel, Field

from .github_loader import chunk_github_files, clone_and_load, validate_github_url
from .health import get_health
from .history import add_qa, get_qa_history
from .rag import answer_with_rag, refactor_suggestions
from .vector_store import VectorStore
from .zip_loader import chunk_files, load_files_from_zip

router = APIRouter()

AUTH_ERROR = (
    "API key is invalid or was rejected. For OpenAI use a key from "
    "https://platform.openai.com/account/api-keys. For OpenRouter set "
    "OPENAI_BASE_URL=https://openrouter.ai/api/v1 and use your OpenRouter key."
)

_vector_store: VectorStore | None = None


def set_vector_store(store: VectorStore) -> None:
    global _vector_store
    _vector_store = store


def get_vector_store() -> VectorStore:
    if _vector_store is None:
        raise RuntimeError("Vector store not initialized")
    return _vector_store


class GitHubIndexRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repo URL")


class QARequest(BaseModel):
    question: str = Field(..., min_length=1)


class QAResponse(BaseModel):
    answer: str
    references: List[dict]
    retrieved_snippets: List[dict]


class HealthResponse(BaseModel):
    status: str
    backend: dict
    vector_db: dict
    llm: dict


def _index_chunks(store: VectorStore, chunks: List[tuple]) -> None:
    """Clear store and add chunks. chunks: (id, file_path, start_line, end_line, text)."""
    store.clear()
    ids = [c[0] for c in chunks]
    docs = [c[4] for c in chunks]
    metadatas = [{"file_path": c[1], "start_line": c[2], "end_line": c[3]} for c in chunks]
    store.add_documents(ids=ids, documents=docs, metadatas=metadatas)


@router.post("/index/zip")
async def index_zip(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a ZIP file")
    content = await file.read()
    if not content:
        raise HTTPException(400, "Upload is empty")
    try:
        files = load_files_from_zip(content)
    except ValueError as e:
        raise HTTPException(400, str(e))
    chunks = chunk_files(files)
    store = get_vector_store()
    try:
        _index_chunks(store, chunks)
    except OpenAIAuthError:
        raise HTTPException(401, AUTH_ERROR)
    return {"status": "ok", "message": "Indexed", "chunks": len(chunks)}


@router.post("/index/github")
async def index_github(body: GitHubIndexRequest) -> dict:
    try:
        url = validate_github_url(body.repo_url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    try:
        files = clone_and_load(url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    chunks = chunk_github_files(files)
    store = get_vector_store()
    try:
        _index_chunks(store, chunks)
    except OpenAIAuthError:
        raise HTTPException(401, AUTH_ERROR)
    return {"status": "ok", "message": "Indexed", "chunks": len(chunks)}


@router.post("/qa", response_model=QAResponse)
async def qa(body: QARequest) -> QAResponse:
    store = get_vector_store()
    if store.count() == 0:
        raise HTTPException(400, "No codebase indexed. Index a ZIP or GitHub repo first.")
    try:
        result = answer_with_rag(store, body.question)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except OpenAIAuthError:
        raise HTTPException(401, AUTH_ERROR)
    add_qa(body.question, result["answer"], result["references"], result["retrieved_snippets"])
    return QAResponse(
        answer=result["answer"],
        references=result["references"],
        retrieved_snippets=result["retrieved_snippets"],
    )


@router.post("/refactor")
async def refactor() -> dict:
    store = get_vector_store()
    if store.count() == 0:
        raise HTTPException(400, "No codebase indexed. Index a ZIP or GitHub repo first.")
    try:
        return refactor_suggestions(store)
    except OpenAIAuthError:
        raise HTTPException(401, AUTH_ERROR)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(**get_health(get_vector_store()))


@router.get("/history")
async def history() -> dict:
    return {"history": get_qa_history()}
