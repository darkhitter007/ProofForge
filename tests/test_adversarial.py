"""Adversarial verifier suite: content tamper, chain reorder, zip-slip, bundle mutate."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

from proofforge.case import init_case, ingest, set_case_metadata
from proofforge.claims import add_claim
from proofforge.verify import verify_case
from proofforge.build import build_case
from proofforge.pack import pack_case
from proofforge.bundle import verify_bundle

CHAIN_FAILURE_CODES = {
    "CASE_IDENTITY_MISMATCH",
    "CHAIN_SEQUENCE_MISMATCH",
    "CHAIN_PREV_HASH_MISMATCH",
    "CHAIN_HEAD_MISMATCH",
}


def prepare(tmp_path: Path):
    ws = tmp_path / "cases"
    ev = tmp_path / "evidence"
    ev.mkdir()
    (ev / "request.txt").write_text("synthetic request")
    (ev / "response.txt").write_text("synthetic response")
    init_case("CASE-001", "Synthetic", ws)
    records = ingest("CASE-001", ev, ws)
    set_case_metadata(
        "CASE-001",
        ws,
        authorization_status="CONFIRMED",
        target="example.invalid",
    )
    add_claim(
        "CASE-001",
        ws,
        "CLAIM-001",
        "Recorded behavior",
        ["evidence/originals/request.txt", "evidence/originals/response.txt"],
        "info",
    )
    return ws, records


def test_adversarial_content_tamper_fails_hash_check(tmp_path):
    ws, records = prepare(tmp_path)
    build_case("CASE-001", ws, strict=True)
    target = ws / "CASE-001" / records[0]["path"]
    target.write_text("tampered")
    result = verify_case("CASE-001", ws)
    codes = {e["code"] for e in result["errors"]}
    assert result["status"] == "FAIL"
    assert "HASH_MISMATCH" in codes
    assert "CASE_IDENTITY_MISMATCH" in codes


def test_adversarial_chain_reorder_fails(tmp_path):
    ws, _ = prepare(tmp_path)
    built = build_case("CASE-001", ws, strict=True)
    original_package_id = built["package_id"]
    chain_path = ws / "CASE-001" / "hashes" / "evidence_chain.jsonl"
    lines = chain_path.read_text().splitlines()
    assert len(lines) >= 2
    chain_path.write_text("\n".join(reversed(lines)) + "\n")
    result = verify_case("CASE-001", ws)
    codes = {e["code"] for e in result["errors"]}
    assert result["status"] == "FAIL"
    assert codes & CHAIN_FAILURE_CODES
    assert result["package_id"] != original_package_id


def test_adversarial_zip_slip_rejected(tmp_path):
    bad = tmp_path / "zip_slip.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("../escape.txt", "no")
    try:
        verify_bundle(bad)
    except ValueError as exc:
        assert "Unsafe archive path" in str(exc)
    else:
        raise AssertionError("zip-slip archive was accepted")


def test_adversarial_bundle_content_tamper_fails(tmp_path):
    ws, _ = prepare(tmp_path)
    build_case("CASE-001", ws, strict=True)
    bundle, identity = pack_case("CASE-001", ws)
    assert verify_bundle(bundle)["status"] == "PASS"
    assert identity["package_id"].startswith("pf2-")

    buf = io.BytesIO()
    with zipfile.ZipFile(bundle, "r") as zin, zipfile.ZipFile(buf, "w") as zout:
        mutated = False
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith("evidence/originals/request.txt"):
                data = b"tampered-in-bundle"
                mutated = True
            zout.writestr(info, data)
        assert mutated, "expected request.txt member in bundle"

    bundle.write_bytes(buf.getvalue())
    result = verify_bundle(bundle)
    codes = {e["code"] for e in result["errors"]}
    assert result["status"] == "FAIL"
    assert "HASH_MISMATCH" in codes
