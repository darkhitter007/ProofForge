from __future__ import annotations
from pathlib import Path
import json
import shutil
from .schema import CaseManifest
from .canonical import canonical_json
from .hashing import sha256_file

CASE_DIRS = [
    "evidence/originals",
    "claims",
    "hashes",
    "validation",
    "export",
]

TEMPLATE_FILES = {
    "AUTHORIZATION.md": "# Authorization\n\nStatus: UNCONFIRMED\n\nDocument the legal scope and authorization here.\n",
    "FINDING.md": "# Finding\n\n## Summary\n\n## Affected component\n\n## Observed behavior\n",
    "REPRODUCTION.md": "# Reproduction\n\n## Preconditions\n\n## Steps\n\n## Expected result\n\n## Actual result\n\n## Cleanup\n",
    "IMPACT.md": "# Impact\n\nState only impacts supported by attached evidence.\n",
    "TIMELINE.md": "# Timeline\n\n",
    "REMEDIATION.md": "# Remediation\n\n",
    "claims/CLAIMS.json": "{\n  \"claims\": []\n}\n",
}

def case_path(case_id: str, workspace: Path) -> Path:
    return workspace / case_id

def init_case(case_id: str, title: str, workspace: Path, force: bool = False) -> Path:
    root = case_path(case_id, workspace)
    if root.exists():
        if not force:
            raise FileExistsError(
                f"Case already exists: {root}. Use --force only for a disposable reset."
            )
        shutil.rmtree(root)
    for rel in CASE_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    manifest = CaseManifest.new(case_id, title).to_dict()
    (root / "CASE_MANIFEST.json").write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    for name, body in TEMPLATE_FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root

def ingest(case_id: str, source: Path, workspace: Path) -> list[dict]:
    root = case_path(case_id, workspace)
    if not root.exists():
        raise FileNotFoundError(f"Unknown case: {case_id}")
    if not source.exists():
        raise FileNotFoundError(source)

    originals = root / "evidence" / "originals"
    records = []
    items = [source] if source.is_file() else [p for p in source.rglob("*") if p.is_file()]
    for src in sorted(items):
        rel = src.name if source.is_file() else str(src.relative_to(source))
        dest = originals / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        records.append({
            "path": str(dest.relative_to(root)).replace("\\", "/"),
            "sha256": sha256_file(dest),
            "size_bytes": dest.stat().st_size,
        })

    manifest_path = root / "hashes" / "evidence_manifest.json"
    manifest_path.write_text(canonical_json({"files": records}) + "\n", encoding="utf-8")
    sums = "\n".join(f'{r["sha256"]}  {r["path"]}' for r in records) + ("\n" if records else "")
    (root / "hashes" / "SHA256SUMS").write_text(sums, encoding="utf-8")
    from .chain import create_chain
    create_chain(case_id, workspace)
    return records

def set_case_metadata(
    case_id: str,
    workspace: Path,
    *,
    authorization_status: str | None = None,
    target: str | None = None,
) -> dict:
    root = case_path(case_id, workspace)
    manifest_path = root / "CASE_MANIFEST.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Unknown case: {case_id}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if authorization_status is not None:
        if authorization_status not in {"UNCONFIRMED", "CONFIRMED"}:
            raise ValueError("authorization_status must be UNCONFIRMED or CONFIRMED")
        manifest["authorization_status"] = authorization_status
    if target is not None:
        manifest["target"] = target
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    return manifest
