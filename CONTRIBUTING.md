# Contributing

```bash
python -m pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
```

Requirements: offline core runtime, deterministic outputs where specified, fail-closed verification, no live-target scanning or exploitation, tests for identity changes, and clean release archives.
