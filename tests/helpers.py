from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def write_flat_session(
    root: Path,
    *,
    frame_spots: tuple[tuple[tuple[float, float, float, float], ...], ...],
    size: tuple[int, int] = (160, 120),
    brightness: float = 190.0,
) -> Path:
    root.mkdir()
    width, height = size
    y, x = np.mgrid[0:height, 0:width]
    illumination = brightness + 18.0 * (x / width) + 10.0 * (y / height)

    for index, spots in enumerate(frame_spots):
        pixels = illumination.copy()
        for center_x, center_y, radius, strength in spots:
            distance = (x - center_x) ** 2 + (y - center_y) ** 2
            pixels -= strength * np.exp(-distance / (2.0 * radius**2))
        pixels += ((x + 2 * y + index) % 3) - 1
        image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), mode="L")
        image.save(root / f"flat-{index + 1}.png")
    return root


def three_frames(
    *spots: tuple[float, float, float, float],
) -> tuple[tuple[tuple[float, float, float, float], ...], ...]:
    return (spots, spots, spots)
