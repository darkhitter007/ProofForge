from __future__ import annotations
from pathlib import Path
import json
from .case import case_path
from .hashing import sha256_file
from .canonical import canonical_json
from .chain import verify_chain
from .identity import compute_case_identity

REQUIRED_FILES = [
    "CASE_MANIFEST.json",
    "AUTHORIZATION.md",
    "FINDING.md",
    "REPRODUCTION.md",
    "IMPACT.md",
    "TIMELINE.md",
    "REMEDIATION.md",
    "claims/CLAIMS.json",
    "hashes/evidence_chain.jsonl",
    "hashes/evidence_chain_summary.json",
    "hashes/case_identity.json",
]

def verify_case(case_id: str, workspace: Path) -> dict:
    root = case_path(case_id, workspace)
    errors: list[dict] = []
    checks: list[dict] = []

    if not root.exists():
        return {"case_id": case_id, "status": "FAIL", "checks": [], "errors": [{"code": "CASE_NOT_FOUND"}]}

    for rel in REQUIRED_FILES:
        ok = (root / rel).is_file()
        checks.append({"check": "required_file", "path": rel, "ok": ok})
        if not ok:
            errors.append({"code": "MISSING_REQUIRED_FILE", "path": rel})

    evidence_manifest = root / "hashes" / "evidence_manifest.json"
    if evidence_manifest.exists():
        try:
            records = json.loads(evidence_manifest.read_text(encoding="utf-8")).get("files", [])
        except Exception as exc:
            records = []
            errors.append({"code": "INVALID_EVIDENCE_MANIFEST", "detail": str(exc)})
        for record in records:
            rel = record["path"]
            path = root / rel
            if not path.exists():
                errors.append({"code": "MISSING_EVIDENCE", "path": rel})
                checks.append({"check": "evidence_hash", "path": rel, "ok": False})
                continue
            actual = sha256_file(path)
            ok = actual == record["sha256"]
            checks.append({"check": "evidence_hash", "path": rel, "ok": ok})
            if not ok:
                errors.append({
                    "code": "HASH_MISMATCH",
                    "path": rel,
                    "expected": record["sha256"],
                    "actual": actual,
                })
    else:
        checks.append({"check": "evidence_manifest", "ok": False})
        errors.append({"code": "MISSING_EVIDENCE_MANIFEST"})

    chain = verify_chain(case_id, workspace)
    checks.append({"check": "evidence_chain", "ok": chain["ok"]})
    errors.extend(chain.get("errors", []))

    identity_path = root / "hashes" / "case_identity.json"
    package_id = None
    case_root = None
    if identity_path.exists():
        try:
            stored = json.loads(identity_path.read_text(encoding="utf-8"))
            current = compute_case_identity(case_id, workspace)
            package_id = current["package_id"]
            case_root = current["case_root_sha256"]
            ok = (
                stored.get("package_id") == current["package_id"]
                and stored.get("case_root_sha256") == current["case_root_sha256"]
            )
            checks.append({"check": "case_identity", "ok": ok})
            if not ok:
                errors.append({
                    "code": "CASE_IDENTITY_MISMATCH",
                    "expected_package_id": stored.get("package_id"),
                    "actual_package_id": current["package_id"],
                })
        except Exception as exc:
            checks.append({"check": "case_identity", "ok": False})
            errors.append({"code": "INVALID_CASE_IDENTITY", "detail": str(exc)})

    status = "PASS" if not errors else "FAIL"
    passed = sum(1 for c in checks if c.get("ok") is True)
    failed = sum(1 for c in checks if c.get("ok") is False)
    result = {
        "case_id": case_id,
        "status": status,
        "package_id": package_id,
        "case_root_sha256": case_root,
        "summary": {
            "passed_checks": passed,
            "failed_checks": failed,
            "error_count": len(errors),
        },
        "checks": checks,
        "errors": errors,
    }
    out = root / "validation" / "verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(canonical_json(result) + "\n", encoding="utf-8")
    return result
