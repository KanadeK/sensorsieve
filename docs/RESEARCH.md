# Research and differentiation

Research date: 2026-08-30.

## Existing project boundary

The local portfolio was inventoried before selection. It already includes camera/photography tools for focus-shot planning, QR print survival, image sidecars, slow-motion flicker, film batching, screenshot selection, camera-filter rings, and privacy-zone events. It did not contain a camera-sensor flat-field dust detector or cleaning-session comparator.

## Representative alternatives

- [Python-Automatic-Sensor-Dust-Removal](https://github.com/Tschucker/Python-Automatic-Sensor-Dust-Removal) is a small OpenCV/Jupyter project that detects and inpaints dust in photographs. SensorSieve differs by never modifying photographs, requiring repeated calibration captures, reporting persistence, and comparing cleaning sessions.
- [Imatest Flatfield Blemish Detect](https://www.imatest.com/docs/blemish/) is commercial image-quality software that detects visible sensor blemishes and can emit structured results. It validates the real problem, but it is not a small open-source, reproducible CLI focused on household camera-cleaning evidence.
- [CMOS Dust Finder Pro](https://toolkitgen.com/tool/sensor_dust_visualizer) provides a browser upload, enhanced view, and single-image scan. SensorSieve instead uses multi-frame median evidence, deterministic files, explicit capture gates, and before/after classification.
- [Pillow image documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html) documents built-in decompression-bomb protection; SensorSieve retains it and adds file/count/format boundaries.
- [NumPy median documentation](https://numpy.org/doc/stable/reference/generated/numpy.median.html) defines the order statistic used to suppress frame-specific noise and moving scene texture.

## Differentiated promise

SensorSieve answers a narrower question than a photo repair tool: "Which dark features survived across my flat-field captures, and which changed after cleaning?" Its durable outputs are evidence rather than edited images:

- one versioned JSON contract;
- numeric CSV tables;
- annotated overlays tied to the same coordinates;
- clean/review/error exit semantics suitable for scripts;
- explicit uncertainty and no cleaning instructions.

The repository can plausibly attract attention because it addresses a recurring photographer pain with a local, testable workflow and visual demo. Research does not establish or guarantee future stars, adoption, or search traffic.

