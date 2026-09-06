# ProofForge v0.1.3.3 Release Notes

This is a **security release**. Upgrade to **0.1.3.3**.

Earlier public kits **0.1.3.2** and **0.1.3.1** are vulnerable to path escape during verification/identity (crafted relative paths in `evidence_manifest` could cause ProofForge to read/rehash files outside the case root). Do not use them for new work; use tag `v0.1.3.3`.

## Core capabilities

- deterministic package identity
- SHA-256 evidence manifests
- claim-to-evidence mapping
- strict readiness checks
- chained evidence-event verification
- independent ZIP verification
- safe ZIP extraction
- offline standard-library runtime
- adversarial verifier coverage (content tamper, chain reorder, zip-slip)
- path confinement for verify, identity, case_id, and ingest (PATH_ESCAPE)

## What changed in 0.1.3.3

- **Security fix:** confine paths so `verify_case` / `compute_case_identity` cannot hash outside the case (`PATH_ESCAPE`)
- Harden `case_id` validation and ingest destination/symlink handling
- New `src/proofforge/paths.py` helpers (`ensure_within`, `safe_join`, `validate_case_id`)
- Path-safety tests in `tests/test_path_safety.py`
- Version and release provenance aligned on tag `v0.1.3.3`

## Known limitations

- no trusted timestamp authority
- no external researcher identity attestation
- no hardware-backed signing
- no automatic submission
- no vulnerability discovery or live-target interaction
