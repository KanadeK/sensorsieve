# Failure and repair guide

SensorSieve fails fast with exit code `2` when it cannot support the promised analysis. Keep the command unchanged while fixing the named boundary.

## Input and capture failures

| Message contains | Cause | Repair |
|---|---|---|
| `input must be a real directory` | Missing path, file path, or directory symlink | Pass one local real directory |
| `at least 3` | Too few supported images | Add a third same-session JPEG/PNG capture |
| `more than 32` | Unbounded batch | Split images into coherent sessions of at most 32 |
| `matching dimensions` | Crop, orientation, or export sizes differ | Re-export the session at one unchanged pixel size |
| `cannot decode` | Corrupt or forged JPEG/PNG | Open/re-export that named file; do not rename another format |
| `mean luminance` | Capture is too dark or near-white | Retake with a bright, non-clipped exposure |
| `clipped pixels` | Large black/white regions | Retake against a more even surface/exposure |
| `residual mask covers` | Texture or illumination variation dominates | Defocus, move between captures, and use a smoother flat field |

## Output failures

SensorSieve writes only to a missing or empty directory. Choose a new path instead of deleting owner data:

```powershell
uv run sensorsieve inspect .\my-session --output .\report-2
```

It rejects file paths, symlinks, nonempty directories, and missing parent directories.

## Development environment failures

If this Windows host cannot initialize uv's global cache, keep the project command the same and use the repository-local cache:

```powershell
uv --cache-dir .uv-cache sync --extra dev
pwsh -NoProfile -File scripts/check.ps1
```

If PyPI access fails with a socket permission error, rerun the unchanged command in a network-enabled shell or CI. Do not remove the dependency audit or loosen the lock.

If a test fails, run the named focused file first, repair the root cause, and then rerun the full gate:

```powershell
uv --cache-dir .uv-cache run --extra dev pytest tests/test_detection.py -q
pwsh -NoProfile -File scripts/check.ps1
```

Do not delete assertions, lower coverage, ignore failed examples, or treat a locally built wheel as a published Release.

