#!/usr/bin/env bash
set -euo pipefail
CASE_ID="JUDGE-001"
RESULTS="demo_results.json"
TMP_BASE="${TMPDIR:-$HOME/.tmp}"
mkdir -p "$TMP_BASE"

python - <<'PY'
import json
from pathlib import Path
Path("demo_results.json").write_text(json.dumps({"steps":[]}, indent=2)+"\n")
PY

record_step() {
  python - "$1" "$2" "$3" <<'PY'
import json, sys
from pathlib import Path
p=Path("demo_results.json")
d=json.loads(p.read_text())
name, expected, actual=sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d["steps"].append({"name":name,"expected_exit":expected,"actual_exit":actual,"ok":expected==actual})
d["status"]="PASS" if all(s["ok"] for s in d["steps"]) else "FAIL"
p.write_text(json.dumps(d, indent=2)+"\n")
PY
}

proofforge demo-reset "$CASE_ID" --title "Synthetic access-control regression"
proofforge ingest "$CASE_ID" ./demo_evidence
proofforge set-meta "$CASE_ID" --authorization CONFIRMED --target example.invalid
proofforge claim-add "$CASE_ID" --id CLAIM-001 --text "The synthetic request and response correspond to the recorded endpoint behavior." --evidence evidence/originals/request.txt --evidence evidence/originals/response.txt --severity info
proofforge build "$CASE_ID" --strict
proofforge verify "$CASE_ID"; record_step clean_case_verifies 0 $?
bundle=$(proofforge pack "$CASE_ID" | head -n 1)
proofforge verify-bundle "$bundle"; record_step bundle_verifies 0 $?

cp "cases/$CASE_ID/evidence/originals/request.txt" "$TMP_BASE/pf_req.good"
printf '\nTAMPERED\n' >> "cases/$CASE_ID/evidence/originals/request.txt"
set +e; proofforge verify "$CASE_ID"; rc=$?; set -e
record_step content_tamper_fails 1 "$rc"
mv "$TMP_BASE/pf_req.good" "cases/$CASE_ID/evidence/originals/request.txt"

cp "cases/$CASE_ID/hashes/evidence_chain.jsonl" "$TMP_BASE/pf_chain.good"
tac "cases/$CASE_ID/hashes/evidence_chain.jsonl" > "$TMP_BASE/pf_chain.rev"
mv "$TMP_BASE/pf_chain.rev" "cases/$CASE_ID/hashes/evidence_chain.jsonl"
set +e; proofforge verify "$CASE_ID"; rc=$?; set -e
record_step chain_reorder_fails 1 "$rc"
mv "$TMP_BASE/pf_chain.good" "cases/$CASE_ID/hashes/evidence_chain.jsonl"

proofforge verify "$CASE_ID"; record_step restored_case_verifies 0 $?
python - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("demo_results.json").read_text())
print(json.dumps(d, indent=2))
raise SystemExit(0 if d.get("status")=="PASS" else 1)
PY
echo "ProofForge v0.1.3.1 judge demo complete."
