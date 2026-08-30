# Contributing

SensorSieve keeps one narrow contract: repeated local flat-field images in, deterministic evidence artifacts out. Please open an issue before proposing a new format, correction workflow, GUI, or remote integration.

## Setup

```powershell
git clone https://github.com/KanadeK/sensorsieve.git
cd sensorsieve
uv --cache-dir .uv-cache sync --extra dev
pwsh -NoProfile -File scripts/check.ps1
```

## Change rules

- Add a failing behavior test before changing logic.
- Validate external data only at the CLI/image/output boundaries.
- Never modify source photographs or copy source paths/EXIF into reports.
- Keep schema and exit-code changes explicit in `SPEC.md` and `CHANGELOG.md`.
- Do not add a runtime dependency unless the current stack cannot solve the accepted requirement.
- Run the full gate before every commit and do not skip or weaken a failing check.

Commits use `feat:`, `fix:`, `test:`, `docs:`, or `chore:` prefixes and contain one logical change.

