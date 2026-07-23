from __future__ import annotations
from pathlib import Path
import json
from .case import case_path
from .claims import load_claims

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def export_case(case_id: str, workspace: Path, format_name: str) -> Path:
    root = case_path(case_id, workspace)
    manifest = json.loads((root / "CASE_MANIFEST.json").read_text(encoding="utf-8"))
    evidence_path = root / "hashes" / "evidence_manifest.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {"files": []}
    claims = load_claims(case_id, workspace)

    title = manifest["title"]
    if format_name == "hackerone":
        filename = "hackerone_report.md"
        heading = "# Vulnerability Report"
    elif format_name == "generic":
        filename = "generic_disclosure.md"
        heading = "# Responsible Disclosure Report"
    else:
        raise ValueError("format must be 'hackerone' or 'generic'")

    evidence_lines = "\n".join(
        f'- `{item["path"]}` | SHA-256 `{item["sha256"]}`'
        for item in evidence.get("files", [])
    ) or "- No evidence recorded."

    claim_lines = "\n".join(
        f'- **{c["claim_id"]}** [{c["severity"]}]: {c["text"]}\n'
        + "".join(f'  - Evidence: `{p}`\n' for p in c.get("evidence_paths", []))
        for c in claims
    ) or "- No structured claims recorded."

    body = f"""{heading}

## Title

{title}

## Case ID

`{case_id}`

## Authorization

{_read(root / "AUTHORIZATION.md")}

## Finding

{_read(root / "FINDING.md")}

## Structured Claims

{claim_lines}

## Reproduction

{_read(root / "REPRODUCTION.md")}

## Impact

{_read(root / "IMPACT.md")}

## Evidence

{evidence_lines}

## Timeline

{_read(root / "TIMELINE.md")}

## Remediation

{_read(root / "REMEDIATION.md")}
"""
    out = root / "export" / filename
    out.write_text(body, encoding="utf-8")
    return out
