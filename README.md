# ProofForge

**v0.1.3.1** — Verifiable evidence packages for authorized security disclosures.

ProofForge turns user-supplied disclosure evidence into a deterministic, independently verifiable package with a chained proof trail and a stable package identity.

It **does** organize evidence, map claims to files, build and pack a case, and verify the result offline. It **does not** scan targets, exploit systems, evade controls, or submit reports automatically.

## Hero demo (real verifier codes)

Clean build + verify (or run `./scripts/judge_demo.sh`):

```bash
python -m pip install -e ".[dev]"
proofforge demo-reset JUDGE-001 --title "Synthetic access-control regression"
proofforge ingest JUDGE-001 ./demo_evidence
proofforge set-meta JUDGE-001 --authorization CONFIRMED --target example.invalid
proofforge claim-add JUDGE-001 --id CLAIM-001 \
  --text "Recorded endpoint behavior." \
  --evidence evidence/originals/request.txt \
  --evidence evidence/originals/response.txt \
  --severity info
proofforge build JUDGE-001 --strict
proofforge verify JUDGE-001
# status: PASS
```

Content tamper → `HASH_MISMATCH` (and usually `CASE_IDENTITY_MISMATCH`):

```bash
printf '\nTAMPERED\n' >> cases/JUDGE-001/evidence/originals/request.txt
proofforge verify JUDGE-001
# status: FAIL
# errors include: HASH_MISMATCH, CASE_IDENTITY_MISMATCH
```

Chain reorder → identity and/or chain sequence failures:

```bash
# reverse lines in hashes/evidence_chain.jsonl
proofforge verify JUDGE-001
# status: FAIL
# errors include: CASE_IDENTITY_MISMATCH and/or
#   CHAIN_SEQUENCE_MISMATCH / CHAIN_PREV_HASH_MISMATCH / CHAIN_HEAD_MISMATCH
```

Zip-slip → rejected before extract:

```bash
# archive member path escapes destination (e.g. ../escape.txt)
proofforge verify-bundle bad.zip
# ValueError: Unsafe archive path: ../escape.txt
```

Adversarial coverage lives in `tests/test_adversarial.py`.

## Quick start

```bash
python -m pip install -e ".[dev]"
chmod +x scripts/judge_demo.sh
./scripts/judge_demo.sh
```

Verify a packed bundle:

```bash
proofforge verify-bundle path/to/JUDGE-001_pf2-..._evidence_bundle.zip
```

## Termux

Keep the repo in Termux private storage, then:

```bash
cd ~/proofforge_v0_1_3_1   # or your checkout path
python -m pip install -e ".[dev]"
chmod +x scripts/judge_demo.sh
./scripts/judge_demo.sh
```

Do not run `python -m pip install --upgrade pip` in Termux.

## Docs

- [THREAT_MODEL.md](THREAT_MODEL.md) — what integrity checks detect (and do not)
- [SECURITY.md](SECURITY.md) — supported release and reporting
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution notes
- [release/](release/) — manifests, field demo results, `SHA256SUMS`
- [RELEASE_NOTES.md](RELEASE_NOTES.md) · [FIELD_VALIDATION.md](FIELD_VALIDATION.md)
