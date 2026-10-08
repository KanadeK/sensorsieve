# Changelog

All notable user-facing changes are documented here.

## [0.1.0] - 2026-10-07

### Added

- Multi-frame JPEG/PNG flat-field validation and persistent dark-feature detection.
- Read-only `inspect` workflow with JSON, CSV, annotated PNG, summary, and stable exit codes.
- Cleaning-session `compare` workflow with resolved, persistent, and new classifications.
- Deterministic synthetic examples, Windows/Linux CI, release packaging, and repair guidance.

### Security

- Updated the development audit toolchain's urllib3 dependency to 2.8.0 to address
  the three September 2026 advisories; runtime image processing dependencies are unchanged.
