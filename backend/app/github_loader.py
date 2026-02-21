"""Clone public GitHub repo and load code files."""
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from .zip_loader import (
    CODE_EXTENSIONS,
    MAX_FILE_BYTES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    _decode_utf8,
    _chunk_file,
)

GITHUB_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:/)?(?:\?.*)?$"
)


def normalize_github_url(url: str) -> str:
    u = url.strip()
    if "?" in u:
        u = u.split("?")[0]
    return u.rstrip("/")


def validate_github_url(url: str) -> str:
    normalized = normalize_github_url(url)
    if not GITHUB_URL_PATTERN.match(normalized):
        raise ValueError("Invalid GitHub URL. Use format: https://github.com/owner/repo")
    return normalized


def _is_code_file(path: Path) -> bool:
    if path.suffix.lower() in CODE_EXTENSIONS:
        return True
    if path.name.lower() in ("makefile", "dockerfile", "gemfile", "rakefile"):
        return True
    return False


def clone_and_load(repo_url: str) -> List[Tuple[str, str]]:
    """(file_path, content). Raises ValueError on invalid URL or clone failure."""
    repo_url = validate_github_url(repo_url)
    tmpdir = tempfile.mkdtemp(prefix="codebase_qa_")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmpdir],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            if "fatal:" in err or "not found" in err.lower():
                raise ValueError("Repository not found or not accessible. Ensure it is a public GitHub repo.")
            raise ValueError(f"Git clone failed: {err}")
        root = Path(tmpdir)
        files: List[Tuple[str, str]] = []
        for fpath in root.rglob("*"):
            if not fpath.is_file():
                continue
            rel = fpath.relative_to(root)
            if ".git" in rel.parts or "__MACOSX" in str(rel):
                continue
            if not _is_code_file(rel):
                continue
            try:
                raw = fpath.read_bytes()
            except (OSError, PermissionError):
                continue
            if len(raw) > MAX_FILE_BYTES:
                continue
            text, ok = _decode_utf8(raw)
            if ok and text.strip():
                files.append((str(rel).replace("\\", "/"), text))
        if not files:
            raise ValueError("Repository contains no indexable code files")
        return files
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def chunk_github_files(
    files: List[Tuple[str, str]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Tuple[str, str, int, int, str]]:
    """Same shape as zip_loader.chunk_files."""
    result: List[Tuple[str, str, int, int, str]] = []
    for path, content in files:
        for fp, start, end, text in _chunk_file(path, content, chunk_size, overlap):
            result.append((f"{fp}:{start}:{end}", fp, start, end, text))
    return result
