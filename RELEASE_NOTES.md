# ProofForge v0.1.3.1 Release Notes

This is ProofForge's first public release candidate.

## Core capabilities

- deterministic package identity
- SHA-256 evidence manifests
- claim-to-evidence mapping
- strict readiness checks
- chained evidence-event verification
- independent ZIP verification
- safe ZIP extraction
- offline standard-library runtime

## Cleanup in this release

- baked in Termux `$TMPDIR` handling
- removed caches and compiled bytecode
- added public-release documentation
- added field-validation evidence
- regenerated checksums

## Known limitations

- no trusted timestamp authority
- no external researcher identity attestation
- no hardware-backed signing
- no automatic submission
- no vulnerability discovery or live-target interaction
