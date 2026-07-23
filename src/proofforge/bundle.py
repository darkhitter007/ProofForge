from __future__ import annotations
from pathlib import Path
import tempfile, zipfile
from .verify import verify_case

def _safe_extract(zf: zipfile.ZipFile, destination: Path) -> None:
    base = destination.resolve()
    for m in zf.infolist():
        target = (destination / m.filename).resolve()
        if target != base and base not in target.parents:
            raise ValueError(f"Unsafe archive path: {m.filename}")
    zf.extractall(destination)

def verify_bundle(bundle_path: Path) -> dict:
    if not bundle_path.exists():
        return {"status":"FAIL","bundle":str(bundle_path),"errors":[{"code":"BUNDLE_NOT_FOUND"}]}
    if not zipfile.is_zipfile(bundle_path):
        return {"status":"FAIL","bundle":str(bundle_path),"errors":[{"code":"INVALID_ZIP"}]}
    with tempfile.TemporaryDirectory(prefix="proofforge-verify-") as td:
        root = Path(td)
        with zipfile.ZipFile(bundle_path) as zf:
            _safe_extract(zf, root)
        cases = [p for p in root.rglob("*") if p.is_dir() and (p/"CASE_MANIFEST.json").is_file()]
        if len(cases) != 1:
            return {"status":"FAIL","bundle":str(bundle_path),
                    "errors":[{"code":"AMBIGUOUS_OR_MISSING_CASE_ROOT","case_root_count":len(cases)}]}
        case_root = cases[0]
        result = verify_case(case_root.name, case_root.parent)
        return {
            "status": result["status"], "bundle": str(bundle_path), "case_id": case_root.name,
            "package_id": result.get("package_id"), "case_root_sha256": result.get("case_root_sha256"),
            "summary": result.get("summary"), "errors": result.get("errors", []),
        }
