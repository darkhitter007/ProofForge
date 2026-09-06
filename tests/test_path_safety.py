"""Path confinement: case_id escape, evidence path escape, zip-slip, symlink ingest."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from proofforge.case import case_path, init_case, ingest, set_case_metadata
from proofforge.paths import ensure_within, safe_join, validate_case_id
from proofforge.verify import verify_case
from proofforge.bundle import verify_bundle
from proofforge.build import build_case
from proofforge.claims import add_claim


def _prepare(tmp_path: Path):
    ws = tmp_path / "cases"
    ev = tmp_path / "evidence"
    ev.mkdir()
    (ev / "request.txt").write_text("synthetic request")
    init_case("CASE-001", "Synthetic", ws)
    ingest("CASE-001", ev, ws)
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
        ["evidence/originals/request.txt"],
        "info",
    )
    build_case("CASE-001", ws, strict=True)
    return ws


def test_validate_case_id_rejects_traversal():
    for bad in ("..", ".", "../x", "a/b", "a\\b", "", "  x", "x  ", "x\x00y", "~/x"):
        with pytest.raises(ValueError):
            validate_case_id(bad)


def test_case_path_rejects_escape(tmp_path):
    ws = tmp_path / "cases"
    ws.mkdir()
    with pytest.raises(ValueError):
        case_path("..", ws)
    with pytest.raises(ValueError):
        case_path("../escape", ws)
    with pytest.raises(ValueError):
        case_path("foo/bar", ws)


def test_safe_join_rejects_escape(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "ok.txt").write_text("in")
    assert safe_join(root, "ok.txt").is_file()
    with pytest.raises(ValueError):
        safe_join(root, "../../etc/passwd")
    with pytest.raises(ValueError):
        safe_join(root, "..", "passwd")
    with pytest.raises(ValueError):
        safe_join(root, "/etc/passwd")


def test_verify_rejects_manifest_path_escape_without_hashing_outside(tmp_path):
    """Crafted evidence_manifest path must PATH_ESCAPE — never HASH_MISMATCH on outside file."""
    ws = _prepare(tmp_path)
    outside = tmp_path / "outside_secret.txt"
    outside.write_text("TOP_SECRET_OUTSIDE_CASE")
    case_root = ws / "CASE-001"
    # case is tmp_path/cases/CASE-001 → ../../outside_secret.txt == tmp_path/outside_secret.txt
    escape_rel = "../../outside_secret.txt"
    assert (case_root / escape_rel).resolve() == outside.resolve()

    manifest_path = case_root / "hashes" / "evidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fake_hash = "0" * 64
    manifest["files"] = [{"path": escape_rel, "sha256": fake_hash, "size_bytes": 1}]
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    result = verify_case("CASE-001", ws)
    codes = {e["code"] for e in result["errors"]}
    assert result["status"] == "FAIL"
    assert "PATH_ESCAPE" in codes
    assert "HASH_MISMATCH" not in codes


def test_ingest_rejects_dotdot_relative_name(tmp_path):
    ws = tmp_path / "cases"
    init_case("CASE-002", "T", ws)
    src = tmp_path / "ev"
    src.mkdir()
    (src / "ok.txt").write_text("x")
    records = ingest("CASE-002", src, ws)
    assert all(".." not in r["path"] for r in records)


def test_ingest_rejects_symlink_source(tmp_path):
    ws = tmp_path / "cases"
    init_case("CASE-003", "T", ws)
    real = tmp_path / "real.txt"
    real.write_text("secret")
    link = tmp_path / "link.txt"
    link.symlink_to(real)
    with pytest.raises(ValueError, match="symlink"):
        ingest("CASE-003", link, ws)


def test_ingest_rejects_symlink_inside_tree(tmp_path):
    ws = tmp_path / "cases"
    init_case("CASE-004", "T", ws)
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "ok.txt").write_text("ok")
    outside = tmp_path / "outside.txt"
    outside.write_text("nope")
    (tree / "sneaky.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        ingest("CASE-004", tree, ws)


def test_zip_slip_still_rejected(tmp_path):
    bad = tmp_path / "zip_slip.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("../escape.txt", "no")
    with pytest.raises(ValueError, match="Unsafe archive path"):
        verify_bundle(bad)


def test_ensure_within(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    inner = root / "a" / "b"
    inner.mkdir(parents=True)
    assert ensure_within(root, inner) == inner.resolve()
    with pytest.raises(ValueError):
        ensure_within(root, tmp_path / "other")
