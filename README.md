# ProofForge v0.1.3.1

ProofForge creates deterministic, independently verifiable evidence packages for authorized security disclosures.

It does not scan targets, exploit systems, evade controls, or submit reports automatically. It organizes user-supplied evidence, maps claims to evidence, builds a chained proof trail, assigns a deterministic package identity, and verifies the resulting bundle offline.

## Quick start

```bash
python -m pip install -e .
chmod +x scripts/judge_demo.sh
./scripts/judge_demo.sh
```

## Verify a bundle

```bash
proofforge verify-bundle path/to/JUDGE-001_pf2-..._evidence_bundle.zip
```

## Termux

Keep the repository in Termux private storage:

```bash
cd ~
unzip -o ~/storage/downloads/ProofForge_v0.1.3.1_Public_Release.zip
cd ~/proofforge_v0_1_3_1
python -m pip install -e .
python -c "import proofforge; print(proofforge.__version__, proofforge.__file__)"
chmod +x scripts/judge_demo.sh
./scripts/judge_demo.sh
```

Do not run `python -m pip install --upgrade pip` in Termux.

See `RELEASE_NOTES.md`, `THREAT_MODEL.md`, `SECURITY.md`, `FIELD_VALIDATION.md`, and `CONTRIBUTING.md`.
