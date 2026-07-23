from __future__ import annotations
from pathlib import Path
import zipfile
from .case import case_path
from .identity import compute_case_identity

def pack_case(case_id: str, workspace: Path) -> tuple[Path, dict]:
    root = case_path(case_id, workspace)
    if not root.exists():
        raise FileNotFoundError(f"Unknown case: {case_id}")
    identity = compute_case_identity(case_id, workspace)
    out = workspace / f"{case_id}_{identity['package_id']}_evidence_bundle.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(workspace)).replace("\\", "/"))
    return out, identity
