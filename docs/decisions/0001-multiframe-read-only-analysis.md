# ADR-0001: Use multi-frame read-only flat-field analysis

## Status

Accepted

## Date

2026-08-30

## Context

A single bright-wall photograph can contain sensor dust, wall texture, lighting gradients, JPEG noise, or scene shadows. Automatically editing ordinary photographs would increase the consequences of a false positive and would overlap existing inpainting tools. The first release also needs to run offline on Windows and Linux with reproducible sample data.

## Decision

Require at least three same-size JPEG/PNG flat-field captures. Normalize every frame against a smooth illumination estimate, aggregate residual darkness with a median, require frame persistence, and emit reports plus overlays. Keep source images read-only. Compare two independently analyzed sessions by normalized spot coordinates.

Pillow and NumPy are the only runtime dependencies. The CLI owns the validation boundary and exposes schema-versioned JSON plus stable exit codes.

## Alternatives considered

### Single-image contrast enhancement

- Pro: simplest interaction.
- Con: cannot distinguish persistent sensor features from scene texture or transient noise.
- Rejected: it weakens the core evidence claim.

### Automatic inpainting

- Pro: immediately produces cosmetically repaired photos.
- Con: destructive derivative generation, false-positive risk, and direct overlap with existing projects.
- Rejected: cleaning evidence, not photo editing, is the product.

### OpenCV and SciPy pipeline

- Pro: large set of ready-made morphology and component functions.
- Con: more runtime dependencies than the bounded algorithm needs.
- Rejected: Pillow plus NumPy is sufficient; connected components remain a small explicit implementation.

## Consequences

- Users must deliberately capture a short calibration session.
- The result is stronger evidence than a one-frame visualization but is not laboratory calibration.
- Downsampling bounds memory and runtime; very small defects may be missed at the default analysis size.
- New formats or correction features require a new decision rather than silently widening v0.1 behavior.

