from pathlib import Path
import zipfile
from proofforge.case import init_case, ingest, set_case_metadata
from proofforge.claims import add_claim
from proofforge.verify import verify_case
from proofforge.build import build_case
from proofforge.pack import pack_case
from proofforge.bundle import verify_bundle

def prepare(tmp_path: Path):
    ws=tmp_path/"cases"; ev=tmp_path/"evidence"; ev.mkdir()
    (ev/"request.txt").write_text("synthetic request")
    (ev/"response.txt").write_text("synthetic response")
    init_case("CASE-001","Synthetic",ws)
    records=ingest("CASE-001",ev,ws)
    set_case_metadata("CASE-001",ws,authorization_status="CONFIRMED",target="example.invalid")
    add_claim("CASE-001",ws,"CLAIM-001","Recorded behavior",
              ["evidence/originals/request.txt","evidence/originals/response.txt"],"info")
    return ws,records

def test_chain_is_bound_to_identity(tmp_path):
    ws,_=prepare(tmp_path)
    built=build_case("CASE-001",ws,strict=True)
    assert built["package_id"].startswith("pf2-")
    original=built["package_id"]
    p=ws/"CASE-001/hashes/evidence_chain.jsonl"
    lines=p.read_text().splitlines()
    p.write_text("\n".join(reversed(lines))+"\n")
    result=verify_case("CASE-001",ws)
    codes={e["code"] for e in result["errors"]}
    assert result["status"]=="FAIL"
    assert "CASE_IDENTITY_MISMATCH" in codes
    assert result["package_id"] != original

def test_bundle_verifier(tmp_path):
    ws,_=prepare(tmp_path)
    build_case("CASE-001",ws,strict=True)
    bundle, ident=pack_case("CASE-001",ws)
    result=verify_bundle(bundle)
    assert result["status"]=="PASS"
    assert result["package_id"]==ident["package_id"]

def test_unsafe_zip_rejected(tmp_path):
    bad=tmp_path/"bad.zip"
    with zipfile.ZipFile(bad,"w") as z:
        z.writestr("../escape.txt","no")
    try:
        verify_bundle(bad)
    except ValueError as e:
        assert "Unsafe archive path" in str(e)
    else:
        raise AssertionError("unsafe zip accepted")

def test_content_tamper(tmp_path):
    ws,records=prepare(tmp_path)
    build_case("CASE-001",ws,strict=True)
    (ws/"CASE-001"/records[0]["path"]).write_text("tampered")
    result=verify_case("CASE-001",ws)
    codes={e["code"] for e in result["errors"]}
    assert "HASH_MISMATCH" in codes
    assert "CASE_IDENTITY_MISMATCH" in codes
