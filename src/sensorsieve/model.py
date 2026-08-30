from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatImage = NDArray[np.float32]
ByteImage = NDArray[np.uint8]


@dataclass(frozen=True)
class ImageSession:
    filenames: tuple[str, ...]
    original_width: int
    original_height: int
    analysis_width: int
    analysis_height: int
    frames: FloatImage


@dataclass(frozen=True)
class Spot:
    spot_id: int
    image_x: float
    image_y: float
    sensor_x: float
    sensor_y: float
    bbox_left: float
    bbox_top: float
    bbox_right: float
    bbox_bottom: float
    area_pixels: int
    mean_contrast: float
    peak_contrast: float
    persistence: float


@dataclass(frozen=True)
class DetectionResult:
    session: ImageSession
    threshold: float
    spots: tuple[Spot, ...]
    median_frame: ByteImage
    residual_map: FloatImage


@dataclass(frozen=True)
class SpotMatch:
    before: Spot
    after: Spot
    distance: float


@dataclass(frozen=True)
class ComparisonResult:
    before: DetectionResult
    after: DetectionResult
    resolved: tuple[Spot, ...]
    persistent: tuple[SpotMatch, ...]
    new: tuple[Spot, ...]
