from __future__ import annotations
from pathlib import Path
import json
from .case import case_path
from .canonical import canonical_json
from .claims import load_claims
from .identity import write_case_identity
from .chain import verify_chain

def build_case(case_id: str, workspace: Path, strict: bool = False) -> dict:
    root = case_path(case_id, workspace)
    if not root.exists():
        raise FileNotFoundError(f"Unknown case: {case_id}")

    manifest = json.loads((root / "CASE_MANIFEST.json").read_text(encoding="utf-8"))
    evidence_path = root / "hashes" / "evidence_manifest.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {"files": []}
    evidence_paths = {item.get("path") for item in evidence.get("files", [])}
    claims = load_claims(case_id, workspace)

    claim_checks = []
    unsupported_claims = []
    for claim in claims:
        refs = claim.get("evidence_paths", [])
        missing = sorted(ref for ref in refs if ref not in evidence_paths)
        supported = bool(refs) and not missing
        row = {
            "claim_id": claim.get("claim_id"),
            "supported": supported,
            "evidence_paths": refs,
            "missing_evidence_paths": missing,
        }
        claim_checks.append(row)
        if not supported:
            unsupported_claims.append(claim.get("claim_id"))

    warnings = []
    blockers = []
    authorization_confirmed = manifest.get("authorization_status") == "CONFIRMED"
    target_specified = manifest.get("target") not in ("", "UNSPECIFIED")
    evidence_count = len(evidence.get("files", []))
    chain_result = verify_chain(case_id, workspace)

    if not authorization_confirmed:
        warnings.append("Authorization remains UNCONFIRMED.")
        if strict:
            blockers.append("AUTHORIZATION_UNCONFIRMED")
    if not target_specified:
        warnings.append("Target remains UNSPECIFIED.")
        if strict:
            blockers.append("TARGET_UNSPECIFIED")
    if evidence_count == 0:
        warnings.append("No evidence has been ingested.")
        if strict:
            blockers.append("NO_EVIDENCE")
    if unsupported_claims:
        warnings.append(f"Unsupported claims: {', '.join(unsupported_claims)}")
        if strict:
            blockers.append("UNSUPPORTED_CLAIMS")
    if not chain_result["ok"]:
        warnings.append("Evidence chain verification failed.")
        if strict:
            blockers.append("EVIDENCE_CHAIN_INVALID")

    identity = None
    if evidence_count > 0 and chain_result["ok"]:
        identity = write_case_identity(case_id, workspace)

    result = {
        "case_id": case_id,
        "status": "BLOCKED" if blockers else "READY",
        "strict": strict,
        "authorization_confirmed": authorization_confirmed,
        "target_specified": target_specified,
        "evidence_count": evidence_count,
        "claim_count": len(claims),
        "claim_checks": claim_checks,
        "chain": chain_result,
        "package_id": identity["package_id"] if identity else None,
        "case_root_sha256": identity["case_root_sha256"] if identity else None,
        "warnings": warnings,
        "blockers": blockers,
    }

    out = root / "validation" / "completeness.json"
    out.write_text(canonical_json(result) + "\n", encoding="utf-8")
    return result
