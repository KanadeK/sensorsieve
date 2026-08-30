# Security policy

## Supported version

Security fixes are provided for the latest release line. The initial supported line is `0.1.x`.

## Reporting

Please use GitHub private vulnerability reporting for issues involving crafted images, resource exhaustion, path handling, package integrity, or unintended disclosure. Do not attach private photographs to a public issue.

## Security boundaries

- SensorSieve works offline and has no telemetry, accounts, remote URL loading, or upload endpoint.
- Source directories and photographs are read-only.
- Reports omit absolute paths and EXIF metadata.
- JPEG/PNG encoding, file count, file size, analysis dimensions, decoded dimensions, and capture quality are bounded.
- Pillow decompression-bomb protection stays enabled and warnings become errors.
- Output is limited to documented files in a missing or empty, non-symlink directory.

Pillow and NumPy process untrusted image data inside the invoking user's process. Run the newest compatible SensorSieve patch release and avoid analyzing untrusted files with privileges or filesystem access you do not need.

## Not a physical-safety tool

SensorSieve does not inspect wall construction, camera internals, cleaning tools, or manufacturer procedures. Its mirrored sensor coordinates are guidance only and do not authorize physical cleaning.

