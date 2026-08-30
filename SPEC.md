# Spec: SensorSieve

## Objective

SensorSieve is an offline CLI for photographers who want evidence before and after cleaning a camera sensor. It analyzes at least three flat-field JPEG or PNG captures, separates smooth illumination falloff from dark features that persist across frames, and writes an explainable spot report without modifying the photographs. A comparison command classifies spots as resolved, persistent, or new between two sessions.

The project is successful when a user can run the included dirty/cleaned example, see stable coordinates and annotated overlays, receive honest invalid-capture failures, install the published wheel in a fresh environment, and reproduce the same results on Windows and Linux.

## User-facing contract

```text
sensorsieve inspect INPUT_DIR --output OUTPUT_DIR [--sensitivity FLOAT] [--max-side INT]
sensorsieve compare BEFORE_DIR AFTER_DIR --output OUTPUT_DIR [--sensitivity FLOAT] [--max-side INT]
sensorsieve --version
```

- Input directories contain 3 to 32 non-recursive `.jpg`, `.jpeg`, or `.png` files.
- Files must decode as JPEG or PNG, have matching dimensions within a session, stay below 100 MiB each, and remain within Pillow's decompression-bomb protection.
- Analysis resizes proportionally to at most 2048 pixels on the longest side by default. `--max-side` accepts 512 through 8192.
- `--sensitivity` accepts 2.0 through 12.0 and controls the robust residual threshold; higher values report fewer spots.
- Output directories must not already contain files. Source files are never changed.
- `inspect` writes `report.json`, `spots.csv`, `overlay.png`, and `summary.txt`.
- `compare` writes `report.json`, `changes.csv`, `before-overlay.png`, `after-overlay.png`, and `summary.txt`.
- Exit `0`: no persistent spots for `inspect`, or no persistent/new spots for `compare`.
- Exit `1`: findings need review.
- Exit `2`: usage, input, capture-quality, or output failure.
- JSON reports use `schema_version: 1`; arrays are deterministically ordered.

## Detection semantics

1. Decode, orient from EXIF, convert to grayscale, and resize every frame identically.
2. Reject captures whose mean luminance is below 15% or above 95%, or whose clipped pixels exceed 10%.
3. Estimate the smooth illumination field of each frame with a Gaussian blur.
4. Compute darkness residuals as `max(0, 1 - pixel / smooth_field)`.
5. Take the per-pixel median residual across frames and estimate scale with median absolute deviation (MAD).
6. Threshold at `max(0.012, median + sensitivity * 1.4826 * MAD)`.
7. Group 8-connected pixels, discard components smaller than six analysis pixels, and require at least two-thirds frame persistence at the component center.
8. Report normalized image coordinates plus mirrored physical-sensor guidance coordinates. The physical coordinates are guidance only because camera preview/orientation behavior can differ.
9. Compare sessions by deterministic nearest-neighbor matching within 2.5% of the image diagonal.

SensorSieve detects persistent dark features; it does not prove that a feature is dust, judge whether cleaning is required, or make a cleaning method safe.

## Tech stack

- Python `>=3.11`
- Pillow `>=11,<13` for bounded JPEG/PNG decoding, EXIF orientation, resizing, blur, and overlays
- NumPy `>=2,<3` for median/MAD and array arithmetic
- `argparse` and standard-library CSV/JSON for the public CLI and reports
- Hatchling for wheel/sdist builds

## Commands

- Install: `uv sync --extra dev`
- Focused test: `uv run pytest tests/test_detection.py`
- Tests with coverage: `uv run pytest --cov=sensorsieve --cov-branch --cov-fail-under=90`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format --check .`
- Types: `uv run mypy src tests`
- Build: `uv build`
- Audit: `uv run pip-audit`
- Full release-equivalent gate: `pwsh -NoProfile -File scripts/check.ps1`

## Project structure

```text
src/sensorsieve/       package source
tests/                 unit and CLI integration tests
examples/              deterministic flat-field sessions
docs/                  research, decisions, and repair guidance
scripts/               example, gate, and release packaging automation
tasks/                 implementation plan and completion checklist
.github/workflows/     Windows/Linux CI and tag release
```

## Code style

```python
def normalized_sensor_coordinate(image_coordinate: float) -> float:
    """Mirror a normalized image coordinate for physical-sensor guidance."""
    return round(1.0 - image_coordinate, 6)
```

- Use immutable dataclasses for validated domain values.
- Use explicit exceptions at the CLI boundary; do not catch broad exceptions inside core logic.
- Keep functions small and names domain-specific.
- Serialize decimal values to six places for deterministic reports.

## Testing strategy

- Unit tests generate synthetic gradients and dark spots to prove detection, persistence, matching, and clean cases.
- Boundary tests cover too few files, mixed dimensions, unsupported/forged formats, dark/clipped captures, unsafe output paths, and stable errors.
- CLI tests assert all three exit classes and the exact artifact set.
- Packaging smoke tests install the built wheel and execute the included example.
- Branch coverage must remain at or above 90%; no skipped tests.

## Threat model and boundaries

Trust boundary: image files, filenames, directories, and CLI values are untrusted. Assets at risk are host memory/CPU, output integrity, and local file confidentiality.

- Always: enforce format and size bounds, keep Pillow bomb protection enabled, reject symlinks and mismatched dimensions, escape CSV formula prefixes in text fields, and write only the documented artifacts.
- Already authorized for this task: runtime dependencies above, CI files, repository creation, public GitHub release, and release notification.
- Never: follow symlinks, recurse into arbitrary trees, fetch remote URLs, embed source paths or EXIF metadata in reports, alter originals, or infer a cleaning procedure.

## Success criteria

1. Dirty synthetic session yields at least two stable spots and exit `1`; the cleaned session yields fewer spots.
2. Comparison classifies at least one resolved and one persistent spot with deterministic coordinates.
3. A uniform clean session exits `0`; invalid/hostile boundary fixtures exit `2` with no traceback.
4. Ruff, format, strict mypy, tests with >=90% branch coverage, build, audit, examples, and clean-wheel smoke all pass.
5. GitHub CI passes on Ubuntu and Windows for Python 3.11 and 3.14.
6. `v0.1.0` is an annotated tag with a public non-draft Release containing wheel, sdist, source ZIP, examples ZIP, and `SHA256SUMS`.
7. Downloaded Release assets verify and the wheel runs in a fresh environment; only `KanadeK` appears as contributor.
8. A Gmail completion notice is sent only after criteria 1-7 are verified.

## Non-goals

- RAW/FITS/TIFF support
- Automatic cleaning or photo inpainting
- Camera tethering, EXIF cataloging, cloud upload, or accounts
- Laboratory-grade sensor calibration or manufacturer-specific cleaning advice
- A GUI or hosted service

## Open questions

None blocking. The delegated request authorizes the end-to-end lifecycle; v0.1.0 deliberately keeps the format and command surface narrow.

