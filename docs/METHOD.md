# Detection and comparison method

SensorSieve is designed for explainability rather than a black-box dust score.

## Inspection

1. JPEG/PNG files are sorted by filename, decoded with Pillow safety limits, EXIF-oriented, converted to grayscale, and proportionally bounded by `--max-side`.
2. Every frame must share its original and analysis dimensions and pass mean/clipping capture gates.
3. A Gaussian blur estimates smooth illumination. The per-pixel darkness residual is `max(0, 1 - pixel / smooth)`.
4. The median residual across frames suppresses texture and noise that does not stay at the same sensor coordinate.
5. The detection threshold is the larger of 1.2% darkness or `median + sensitivity * 1.4826 * MAD`.
6. Eight-connected regions smaller than six analysis pixels are discarded. A region must also appear at its center in at least two-thirds of frames.
7. The residual-weighted centroid, bounding box, contrast, and persistence become one deterministic spot record.

If more than 10% of analysis pixels exceed the residual threshold, SensorSieve rejects the session instead of presenting a heavily nonuniform field as a credible dust map.

## Comparison

Sessions must have the same original dimensions. Candidate pairs within 2.5% of the normalized image diagonal are sorted by distance, then by stable spot IDs. The nearest unused pair becomes persistent; unmatched earlier spots are resolved, and unmatched later spots are new.

This is positional evidence, not physical identity proof. A broad blemish can move or change shape enough to fall outside the match radius.

## Determinism

Reports contain no clock, host, absolute path, EXIF, or random value. Files, components, and matches use explicit stable ordering; numeric values are rounded to six decimal places. The release gate regenerates examples and compares CLI output with committed demo artifacts.

