# Implementation plan: SensorSieve v0.1.0

## Overview

Build a new independent Python repository that turns repeated flat-field photos into an offline dust-spot evidence pack and compares cleaning sessions. Deliver it through a verified public GitHub Release and notify the owner only after remote acceptance.

## Architecture decisions

- One validated image boundary feeds pure detection and comparison logic.
- Reports, overlays, and exit codes derive from one typed result model.
- Multi-frame persistence is the authority; no single-image fallback or image-repair path exists.
- Release artifacts are produced from the immutable annotated tag.

## Dependency graph

```text
CLI contract and models
    -> validated image session
        -> residual detection
            -> deterministic reports and overlays
                -> before/after matching
                    -> examples and release gate
                        -> CI, tag, Release, remote acceptance, Gmail
```

## Phase 1: Contract and detection core

### Task 1: Scaffold the package contract

Acceptance: build metadata, rules, spec, research, ADR, and task files define one narrow v0.1.0 surface.

Verification: `uv lock`; inspect `git diff --check`; commit only repository-owned files.

Dependencies: none. Estimated scope: medium.

### Task 2: Detect persistent dark spots

Acceptance: synthetic multi-frame spots are found at stable normalized coordinates; transient marks and clean gradients are excluded; invalid captures fail fast.

Verification: focused RED/GREEN tests, then Ruff and strict mypy.

Dependencies: Task 1. Estimated scope: medium.

### Checkpoint: core

- Package imports and focused tests pass.
- Original fixtures remain byte-identical.

## Phase 2: User workflows

### Task 3: Ship inspect artifacts and CLI

Acceptance: `inspect` writes exactly four deterministic artifacts and returns exits 0/1/2 as specified.

Verification: CLI integration tests and an example run.

Dependencies: Task 2. Estimated scope: medium.

### Task 4: Compare cleaning sessions

Acceptance: deterministic matching classifies resolved, persistent, and new spots and writes the documented artifact set.

Verification: focused comparison and CLI tests.

Dependencies: Tasks 2-3. Estimated scope: medium.

### Checkpoint: workflows

- Dirty, cleaned, clean, and invalid examples exercise all exit classes.
- Machine-readable reports agree with overlays and summaries.

## Phase 3: Release engineering

### Task 5: Complete docs, examples, and local gate

Acceptance: README, repair guide, security policy, contribution guide, changelog, deterministic examples, packaging, and one release-equivalent script are complete.

Verification: full gate passes with >=90% branch coverage and a fresh wheel smoke test.

Dependencies: Tasks 3-4. Estimated scope: medium.

### Task 6: Publish and independently verify v0.1.0

Acceptance: public repo, green cross-platform CI, annotated tag, non-draft Release, exact assets/checksums, downloaded-wheel smoke, contributor hygiene, and Gmail delivery are verified.

Verification: query remote SHAs and workflow conclusions; download assets into an isolated directory; run the public wheel; confirm Gmail in Sent.

Dependencies: Task 5. Estimated scope: medium.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Uneven illumination creates false spots | High | Divide by per-frame smooth field, aggregate median, require persistence |
| Large/malicious images consume resources | High | Fixed formats/count/size, retained Pillow bomb protection, bounded analysis side |
| Coordinates are mistaken for cleaning instructions | Medium | Separate image and mirrored sensor guidance; document uncertainty and no cleaning advice |
| Windows output differs | Medium | Deterministic serialization and Windows/Linux CI |
| GitHub auth is invalid | Medium | Use only the official re-authentication flow and verify state before writes |

## Rollback

Before publication, revert the owning repository's atomic commit. After publication, never move `v0.1.0`; correct defects on `main` and release a new patch tag. GitHub Release deletion is reserved for a security or artifact-integrity emergency.

## Open questions

None blocking.

