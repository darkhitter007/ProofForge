# Threat Model

ProofForge protects the internal integrity and consistency of an authorized disclosure package.

## Detects

- evidence modification or deletion
- evidence-manifest inconsistencies
- chain-event reordering
- broken predecessor links
- chain-head mismatch
- package identity drift
- unsafe ZIP paths

## Does not prevent

- false evidence created before ingestion
- compromise of the host before package creation
- clock manipulation
- identity impersonation
- misleading but internally consistent evidence
