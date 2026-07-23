from __future__ import annotations
from pathlib import Path
import json
from .case import case_path
from .canonical import canonical_json

VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}

def _claims_path(case_id: str, workspace: Path) -> Path:
    return case_path(case_id, workspace) / "claims" / "CLAIMS.json"

def load_claims(case_id: str, workspace: Path) -> list[dict]:
    path = _claims_path(case_id, workspace)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("claims", [])

def add_claim(
    case_id: str,
    workspace: Path,
    claim_id: str,
    text: str,
    evidence_paths: list[str],
    severity: str = "medium",
) -> dict:
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"severity must be one of: {', '.join(sorted(VALID_SEVERITIES))}")
    root = case_path(case_id, workspace)
    if not root.exists():
        raise FileNotFoundError(f"Unknown case: {case_id}")

    claims = load_claims(case_id, workspace)
    if any(c.get("claim_id") == claim_id for c in claims):
        raise ValueError(f"Duplicate claim_id: {claim_id}")

    claim = {
        "claim_id": claim_id,
        "text": text,
        "severity": severity,
        "evidence_paths": sorted(set(evidence_paths)),
    }
    claims.append(claim)
    path = _claims_path(case_id, workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json({"claims": claims}) + "\n", encoding="utf-8")
    return claim
