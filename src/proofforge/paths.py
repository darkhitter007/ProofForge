"""Path confinement helpers: keep case and evidence I/O inside allowed roots."""
from __future__ import annotations

from pathlib import Path


def ensure_within(root: Path, path: Path) -> Path:
    """Resolve *path* and require it to equal *root* or live under it."""
    root_r = root.resolve()
    path_r = path.resolve()
    if path_r != root_r and root_r not in path_r.parents:
        raise ValueError(f"Path escapes allowed root: {path}")
    return path_r


def safe_join(root: Path, *parts: str) -> Path:
    """Join *parts* under *root*, rejecting absolute / empty / ``..`` segments."""
    if not parts:
        raise ValueError("safe_join requires at least one path part")
    segments: list[str] = []
    for part in parts:
        if not isinstance(part, str):
            raise ValueError(f"Path part must be str, got {type(part).__name__}")
        if part == "" or "\x00" in part:
            raise ValueError(f"Unsafe path part: {part!r}")
        p = Path(part)
        if p.is_absolute():
            raise ValueError(f"Absolute path segment not allowed: {part!r}")
        for segment in p.parts:
            if segment in ("", ".", "..") or "\x00" in segment:
                raise ValueError(f"Unsafe path segment: {segment!r}")
            segments.append(segment)
    if not segments:
        raise ValueError(f"Unsafe path parts: {parts!r}")
    return ensure_within(root, root.joinpath(*segments))


def validate_case_id(case_id: str) -> str:
    """Reject case IDs that could escape the workspace via path tricks."""
    if not isinstance(case_id, str) or case_id == "":
        raise ValueError("case_id must be a non-empty string")
    if case_id.strip() != case_id:
        raise ValueError("case_id must not have leading or trailing whitespace")
    if case_id in (".", ".."):
        raise ValueError(f"Invalid case_id: {case_id!r}")
    if any(ch in case_id for ch in ("/", "\\", "\x00")):
        raise ValueError(f"case_id must not contain path separators or null bytes: {case_id!r}")
    if case_id.startswith("~"):
        raise ValueError(f"Invalid case_id: {case_id!r}")
    p = Path(case_id)
    if len(p.parts) != 1 or p.parts[0] != case_id:
        raise ValueError(f"Invalid case_id: {case_id!r}")
    return case_id
