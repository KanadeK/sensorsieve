# SensorSieve

**Find the sensor spots that survive every frame, then prove what changed after cleaning.**

SensorSieve is an offline, read-only CLI for repeated flat-field JPEG/PNG captures. It removes smooth illumination falloff from the analysis, finds dark features that persist across frames, and produces numeric reports plus annotated overlays. The `compare` workflow classifies spots as resolved, persistent, or new.

SensorSieve never edits source photographs and does not provide cleaning instructions. See [SPEC.md](SPEC.md) for the exact v0.1.0 contract and [research](docs/RESEARCH.md) for differentiation from existing tools.

## Development

```powershell
uv sync --extra dev
uv run sensorsieve --version
pwsh -NoProfile -File scripts/check.ps1
```

The complete user quick start and example outputs will be added with the executable workflows in the same release.

