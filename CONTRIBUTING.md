# Contributing to ProofForge

ProofForge favors small, reviewable changes backed by reproducible evidence.

## Development setup

    python -m pip install -e ".[dev]"
    PYTHONPATH=src python -m pytest -q

## Contribution workflow

Use a branch and pull request for changes intended for `main`.

1. Start from an up-to-date `main`.
2. Create a focused working branch.
3. Make the smallest change that solves the intended problem.
4. Run the relevant tests locally.
5. Open a pull request against `main`.
6. Allow GitHub CI to complete.
7. Inspect the test and checksum results.
8. Merge only after the expected evidence is green.

The current CI validates the test suite on Python 3.10, 3.11, and 3.12 and verifies the release checksums.

For a solo maintainer, an additional human approval is not required merely for ceremony. The pull request still provides a useful evidence boundary between a proposed change and the canonical `main` branch.

## Project requirements

Contributions should preserve:

- offline core runtime
- deterministic outputs where specified
- fail-closed verification
- no live-target scanning or exploitation
- tests for identity-affecting changes
- clean release archives

Security-sensitive or release-critical changes should receive additional scrutiny appropriate to their impact.
