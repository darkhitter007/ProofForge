$ErrorActionPreference = "Stop"
proofforge demo-reset
proofforge ingest DEMO-001 .\demo_evidence
proofforge set-meta DEMO-001 --authorization CONFIRMED --target example.invalid
proofforge claim-add DEMO-001 `
  --id CLAIM-001 `
  --text "The synthetic endpoint returned the recorded response." `
  --evidence evidence/originals/request.txt `
  --evidence evidence/originals/response.txt `
  --severity info
proofforge build DEMO-001 --strict
proofforge verify DEMO-001
proofforge export DEMO-001 --format hackerone
proofforge pack DEMO-001
Write-Host "ProofForge v0.1.1 demo complete."
