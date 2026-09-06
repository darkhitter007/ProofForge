# Changelog

## 0.1.3.3
- **Security:** path confinement so verify/identity cannot hash files outside the case root (`PATH_ESCAPE`)
- Harden `case_id` / `case_path` against path-escape tricks (`validate_case_id`)
- Confine ingest destinations and reject symlink collection via `paths.ensure_within` / `safe_join`
- New helpers in `src/proofforge/paths.py` and coverage in `tests/test_path_safety.py`
- Public release provenance via tag `v0.1.3.3` (do not use vulnerable `0.1.3.2` / `0.1.3.1` kits)

## 0.1.3.2
- Adversarial verifier suite (`tests/test_adversarial.py`) covering content/chain/zip-slip failures
- README hero demo with real verifier status codes
- Hygiene carried forward from the 0.1.3.1 documentation/CI line
- Public release provenance via new tag `v0.1.3.2` (historical `v0.1.3.1` tag left untouched)

## 0.1.3.1
- First public release candidate
- Fixed Termux temporary-directory handling
- Added public-release documentation
- Removed cache and bytecode debris
- Added field-validation record

## 0.1.3
- Bound chain files into package identity
- Added `verify-bundle`
- Added safe ZIP extraction and judge demo

## 0.1.2
- Added deterministic package identity and evidence chain

## 0.1.1
- Added claim mapping and strict readiness

## 0.1.0
- Initial release
