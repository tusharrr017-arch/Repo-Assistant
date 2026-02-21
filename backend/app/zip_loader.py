"""Load and chunk code from uploaded ZIP."""
import io
import zipfile
from pathlib import Path
from typing import List, Tuple

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".php",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift", ".scala", ".r", ".R",
    ".sql", ".sh", ".bash", ".zsh", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".md", ".rst", ".txt", ".html", ".css", ".scss", ".vue", ".svelte", ".mjs",
}
MAX_FILE_BYTES = 500_000
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def _is_code_file(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() in CODE_EXTENSIONS:
        return True
    if p.name.lower() in ("makefile", "dockerfile", "gemfile", "rakefile"):
        return True
    return False


def _decode_utf8(content: bytes) -> Tuple[str, bool]:
    try:
        return content.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False


def load_files_from_zip(zip_bytes: bytes) -> List[Tuple[str, str]]:
    """(file_path, content). Raises ValueError if empty or invalid."""
    if not zip_bytes or len(zip_bytes) < 22:
        raise ValueError("Upload is empty or not a valid ZIP file")
    files: List[Tuple[str, str]] = []
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for name in zf.namelist():
                if name.endswith("/") or "__MACOSX" in name or ".git/" in name:
                    continue
                if not _is_code_file(name):
                    continue
                try:
                    raw = zf.read(name)
                except (zipfile.BadZipFile, KeyError, RuntimeError):
                    continue
                if len(raw) > MAX_FILE_BYTES:
                    continue
                text, ok = _decode_utf8(raw)
                if ok and text.strip():
                    files.append((name.lstrip("./"), text))
    except zipfile.BadZipFile:
        raise ValueError("Invalid or corrupted ZIP file")
    if not files:
        raise ValueError("ZIP contains no indexable code files")
    return files


def _chunk_file(
    file_path: str,
    content: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Tuple[str, int, int, str]]:
    """(file_path, start_line, end_line, chunk_text)."""
    lines = content.splitlines()
    if not lines:
        return []
    chunks: List[Tuple[str, int, int, str]] = []
    current_start = 1
    current_lines: List[str] = []
    current_len = 0
    for i, line in enumerate(lines):
        line_num = i + 1
        current_lines.append(line)
        current_len += len(line) + 1
        if current_len >= chunk_size:
            chunks.append((file_path, current_start, line_num, "\n".join(current_lines)))
            overlap_lines = []
            overlap_len = 0
            for j in range(len(current_lines) - 1, -1, -1):
                overlap_lines.insert(0, current_lines[j])
                overlap_len += len(current_lines[j]) + 1
                if overlap_len >= overlap:
                    break
            current_start = line_num - len(overlap_lines) + 1
            current_lines = overlap_lines
            current_len = sum(len(l) + 1 for l in overlap_lines)
    if current_lines:
        chunks.append((file_path, current_start, len(lines), "\n".join(current_lines)))
    return chunks


def chunk_files(
    files: List[Tuple[str, str]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Tuple[str, str, int, int, str]]:
    """(chunk_id, file_path, start_line, end_line, chunk_text)."""
    result: List[Tuple[str, str, int, int, str]] = []
    for path, content in files:
        for fp, start, end, text in _chunk_file(path, content, chunk_size, overlap):
            result.append((f"{fp}:{start}:{end}", fp, start, end, text))
    return result
