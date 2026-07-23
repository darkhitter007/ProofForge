from __future__ import annotations
from pathlib import Path
import hashlib
import json
from .canonical import canonical_json
from .case import case_path

GENESIS = "0" * 64

def _event_hash(event_without_hash: dict) -> str:
    return hashlib.sha256(canonical_json(event_without_hash).encode("utf-8")).hexdigest()

def create_chain(case_id: str, workspace: Path) -> dict:
    root = case_path(case_id, workspace)
    manifest_path = root / "hashes" / "evidence_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("evidence_manifest.json is required")

    records = json.loads(manifest_path.read_text(encoding="utf-8")).get("files", [])
    ordered = sorted(records, key=lambda r: r["path"])

    events = []
    prev_hash = GENESIS
    for index, record in enumerate(ordered):
        body = {
            "chain_schema": 1,
            "sequence": index,
            "event_type": "EVIDENCE_INGESTED",
            "path": record["path"],
            "sha256": record["sha256"],
            "size_bytes": record["size_bytes"],
            "prev_hash": prev_hash,
        }
        event_hash = _event_hash(body)
        event = dict(body)
        event["event_hash"] = event_hash
        events.append(event)
        prev_hash = event_hash

    chain_path = root / "hashes" / "evidence_chain.jsonl"
    chain_path.write_text(
        "".join(canonical_json(event) + "\n" for event in events),
        encoding="utf-8",
    )
    summary = {
        "chain_schema": 1,
        "event_count": len(events),
        "genesis": GENESIS,
        "head_hash": prev_hash,
    }
    (root / "hashes" / "evidence_chain_summary.json").write_text(
        canonical_json(summary) + "\n",
        encoding="utf-8",
    )
    return summary

def verify_chain(case_id: str, workspace: Path) -> dict:
    root = case_path(case_id, workspace)
    chain_path = root / "hashes" / "evidence_chain.jsonl"
    summary_path = root / "hashes" / "evidence_chain_summary.json"
    errors = []

    if not chain_path.exists():
        return {"ok": False, "errors": [{"code": "MISSING_EVIDENCE_CHAIN"}]}
    if not summary_path.exists():
        return {"ok": False, "errors": [{"code": "MISSING_CHAIN_SUMMARY"}]}

    lines = [line for line in chain_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    events = []
    for idx, line in enumerate(lines):
        try:
            events.append(json.loads(line))
        except Exception as exc:
            errors.append({"code": "INVALID_CHAIN_EVENT", "sequence": idx, "detail": str(exc)})

    prev_hash = GENESIS
    for idx, event in enumerate(events):
        if event.get("sequence") != idx:
            errors.append({"code": "CHAIN_SEQUENCE_MISMATCH", "sequence": idx})
        if event.get("prev_hash") != prev_hash:
            errors.append({"code": "CHAIN_PREV_HASH_MISMATCH", "sequence": idx})
        supplied = event.get("event_hash")
        body = dict(event)
        body.pop("event_hash", None)
        actual = _event_hash(body)
        if supplied != actual:
            errors.append({
                "code": "CHAIN_EVENT_HASH_MISMATCH",
                "sequence": idx,
                "expected": supplied,
                "actual": actual,
            })
        prev_hash = supplied or actual

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("event_count") != len(events):
        errors.append({"code": "CHAIN_EVENT_COUNT_MISMATCH"})
    if summary.get("head_hash") != prev_hash:
        errors.append({"code": "CHAIN_HEAD_MISMATCH"})

    return {
        "ok": not errors,
        "event_count": len(events),
        "head_hash": prev_hash,
        "errors": errors,
    }
