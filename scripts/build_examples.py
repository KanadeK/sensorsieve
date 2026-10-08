"""Generate deterministic flat-field sessions used by docs, tests, and release assets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
WIDTH = 320
HEIGHT = 240

SpotSpec = tuple[float, float, float, float]


def _write_session(name: str, frames: tuple[tuple[SpotSpec, ...], ...]) -> None:
    output = EXAMPLES / name
    output.mkdir(parents=True, exist_ok=True)
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH]
    illumination = 185.0 + 24.0 * (x / WIDTH) + 14.0 * (y / HEIGHT)
    expected_names = {f"flat-{index + 1}.png" for index in range(len(frames))}
    for path in output.glob("flat-*.png"):
        if path.name not in expected_names:
            path.unlink()

    for index, spots in enumerate(frames):
        pixels = illumination.copy()
        for center_x, center_y, radius, strength in spots:
            distance = (x - center_x) ** 2 + (y - center_y) ** 2
            pixels -= strength * np.exp(-distance / (2.0 * radius**2))
        pixels += ((x + 2 * y + index) % 3) - 1
        # Remove sub-pixel libm/SIMD differences before truncating to 8-bit samples.
        pixels = np.floor(np.round(np.clip(pixels, 0, 255), decimals=6))
        image = Image.fromarray(pixels.astype(np.uint8), mode="L")
        image.save(output / f"flat-{index + 1}.png", compress_level=9, optimize=False)


def main() -> None:
    resolved = (86.0, 80.0, 8.0, 76.0)
    persistent_before = (230.0, 164.0, 8.0, 72.0)
    persistent_after = (232.0, 164.0, 8.0, 72.0)
    new = (270.0, 58.0, 7.0, 74.0)
    transient = (158.0, 210.0, 8.0, 82.0)

    _write_session(
        "before",
        (
            (resolved, persistent_before, transient),
            (resolved, persistent_before),
            (resolved, persistent_before),
        ),
    )
    _write_session("after", ((persistent_after, new),) * 3)
    _write_session("clean", ((), (), ()))
    _write_session("invalid-too-few", ((resolved,), (resolved,)))
    print("SENSORSIEVE_EXAMPLES=BUILT")


if __name__ == "__main__":
    main()
