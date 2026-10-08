# SensorSieve v0.1.0 release verification

Verified on 2026-10-07 (America/Los_Angeles).

## Public release

- [Repository](https://github.com/KanadeK/sensorsieve): public, MIT, default branch `main`.
- [Release](https://github.com/KanadeK/sensorsieve/releases/tag/v0.1.0): not a draft or prerelease.
- Annotated tag object: `92593438f41683b4c9f0f6f0514b8467d6c7c628`.
- Release code commit: `f192848a7658d6d2d06c60ed7c27f8d98cc74c00`.
- Only contributor: `KanadeK`; private vulnerability reporting is enabled.

## Automated gates

- [main CI](https://github.com/KanadeK/sensorsieve/actions/runs/37738275655):
  Ubuntu and Windows, Python 3.11 and 3.14, all passed.
- [Release workflow](https://github.com/KanadeK/sensorsieve/actions/runs/37738515219):
  four tag gates and packaging/publication all passed.
- 35 tests, 94.29% branch coverage, Ruff, format, strict mypy, builds, dependency
  audit, example regeneration, exact demo artifacts, and installed-wheel smoke passed.
- The development urllib3 lock was updated to 2.8.0 for the September advisories.
- Fixture luminance quantization and uncompressed PNG storage preserve the byte
  checks across the Windows and Linux PNG implementations.

## Downloaded-package acceptance

All five assets were downloaded from public URLs without GitHub authentication:

- `sensorsieve-0.1.0-py3-none-any.whl`
- `sensorsieve-0.1.0.tar.gz`
- `sensorsieve-0.1.0-source.zip`
- `sensorsieve-0.1.0-examples.zip`
- `SHA256SUMS`

All four data-asset checksums matched. The downloaded wheel was installed in a
new Python 3.14.5 environment with NumPy 2.3.5 and Pillow 12.3.0. Actual commands
verified these results:

| Workflow | Result | Exit |
|---|---|---|
| Inspect dirty fixture | 2 persistent spots | 1 |
| Compare fixtures | 1 resolved, 1 persistent, 1 new | 1 |
| Inspect clean fixture | No persistent spots | 0 |
| Inspect two-frame fixture | Rejected; no output directory | 2 |

These are technical checks on synthetic captures. They do not establish physical
sensor cleanliness or a safe cleaning procedure.

Later documentation-only commits on `main` do not move the release tag or replace
its already verified assets.
