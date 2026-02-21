from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router, set_vector_store
from .vector_store import VectorStore

app = FastAPI(
    title="Codebase Q&A with Proof",
    description="Ask questions about your codebase; get answers grounded in retrieved code with file/line references.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
set_vector_store(vector_store)
app.include_router(router, prefix="", tags=["api"])


@app.get("/")
async def root():
    return {"app": "Codebase Q&A with Proof", "docs": "/docs"}
