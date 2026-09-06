from __future__ import annotations
from pathlib import Path
import hashlib, json
from .canonical import canonical_json
from .case import case_path
from .hashing import sha256_file
from .paths import safe_join

IDENTITY_INPUTS = [
    "CASE_MANIFEST.json","AUTHORIZATION.md","FINDING.md","REPRODUCTION.md",
    "IMPACT.md","TIMELINE.md","REMEDIATION.md","claims/CLAIMS.json",
    "hashes/evidence_manifest.json","hashes/evidence_chain.jsonl",
    "hashes/evidence_chain_summary.json",
]

def _entry(root: Path, rel: str) -> dict:
    p = safe_join(root, rel)
    return {"path": rel, "sha256": sha256_file(p), "size_bytes": p.stat().st_size}

def compute_case_identity(case_id: str, workspace: Path) -> dict:
    root = case_path(case_id, workspace)
    missing = []
    for r in IDENTITY_INPUTS:
        try:
            if not safe_join(root, r).is_file():
                missing.append(r)
        except ValueError as exc:
            raise ValueError(f"Identity input path unsafe: {r}") from exc
    if missing:
        raise FileNotFoundError("Missing identity inputs: " + ", ".join(missing))
    manifest = json.loads(safe_join(root, "hashes/evidence_manifest.json").read_text(encoding="utf-8"))
    evidence = sorted(i["path"] for i in manifest.get("files", []))
    inputs = [_entry(root, r) for r in sorted(IDENTITY_INPUTS)]
    inputs += [_entry(root, r) for r in evidence]
    payload = {"identity_schema": 2, "case_id": case_id, "inputs": inputs}
    root_hash = hashlib.sha256(canonical_json(payload).encode()).hexdigest()
    return {
        "identity_schema": 2,
        "case_id": case_id,
        "package_id": f"pf2-{root_hash[:24]}",
        "case_root_sha256": root_hash,
        "input_count": len(inputs),
        "inputs": inputs,
    }

def write_case_identity(case_id: str, workspace: Path) -> dict:
    root = case_path(case_id, workspace)
    result = compute_case_identity(case_id, workspace)
    (root/"hashes/case_identity.json").write_text(canonical_json(result)+"\n", encoding="utf-8")
    return result
