# ProofForge v0.1.3.2 Release Notes

This is the current public release kit for ProofForge.

The historical tag `v0.1.3.1` remains on an earlier tree and is not moved; use `v0.1.3.2` for the current kit.

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

## What changed in 0.1.3.2

- adversarial verifier suite and README hero demo
- repo hygiene from the 0.1.3.1 documentation/CI line
- version and release provenance aligned on tag `v0.1.3.2`

## Known limitations

- no trusted timestamp authority
- no external researcher identity attestation
- no hardware-backed signing
- no automatic submission
- no vulnerability discovery or live-target interaction
