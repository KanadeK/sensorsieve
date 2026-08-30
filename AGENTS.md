# SensorSieve agent guide

## Tech stack

- Python 3.11+
- Pillow and NumPy at runtime
- pytest, Ruff, strict mypy, build, and pip-audit for development
- `uv` owns dependency resolution and the committed `uv.lock`

## Commands

- Sync: `uv sync --extra dev`
- Focused tests: `uv run pytest tests/test_detection.py`
- Full gate: `pwsh -NoProfile -File scripts/check.ps1`
- Build: `uv build`

## Conventions

- Keep CLI parsing, image-boundary validation, detection, comparison, and reporting in separate modules.
- Validate paths, formats, dimensions, and resource limits once at the image-loading boundary.
- Internal functions trust validated typed values; do not scatter defensive fallbacks.
- Reports are deterministic and schema-versioned. Never include timestamps or machine-specific absolute paths.
- Tests assert observable inputs, outputs, and exit codes rather than implementation calls.

## Boundaries

- Always keep source images read-only and write only inside a new, empty output directory.
- Always preserve exit codes: `0` clean, `1` spots need review, `2` invalid input or operational failure.
- Never inpaint, clean, rename, or rewrite source images.
- Never add telemetry, uploads, accounts, AI services, or camera-control features.
- Never weaken failing tests, coverage, type checks, audits, or cross-platform CI to make a gate pass.

