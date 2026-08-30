from __future__ import annotations

from collections import deque
from dataclasses import replace

import numpy as np
from PIL import Image, ImageFilter

from sensorsieve.errors import CaptureQualityError
from sensorsieve.model import DetectionResult, FloatImage, ImageSession, Spot

_MIN_COMPONENT_AREA = 6
_MIN_PERSISTENCE = 2 / 3


def _residual_for(frame: FloatImage) -> FloatImage:
    height, width = frame.shape
    radius = max(6.0, min(width, height) / 24.0)
    source = Image.fromarray(np.rint(frame * 255).astype(np.uint8), mode="L")
    smooth_image = source.filter(ImageFilter.GaussianBlur(radius=radius))
    smooth = np.asarray(smooth_image, dtype=np.float32) / np.float32(255.0)
    residual = np.maximum(np.float32(0.0), np.float32(1.0) - frame / smooth)
    return residual.astype(np.float32, copy=False)


def _threshold(residual: FloatImage, sensitivity: float) -> float:
    height, width = residual.shape
    border = max(2, min(height, width) // 50)
    core = residual[border : height - border, border : width - border]
    baseline = float(np.median(core))
    mad = float(np.median(np.abs(core - baseline)))
    return max(0.012, baseline + sensitivity * 1.4826 * mad)


def _components(
    mask: np.ndarray[tuple[int, int], np.dtype[np.bool_]],
) -> list[list[tuple[int, int]]]:
    remaining = {tuple(point) for point in np.argwhere(mask)}
    components: list[list[tuple[int, int]]] = []
    while remaining:
        start = remaining.pop()
        queue = deque([start])
        component = [start]
        while queue:
            y, x = queue.popleft()
            for next_y in range(y - 1, y + 2):
                for next_x in range(x - 1, x + 2):
                    neighbor = (next_y, next_x)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        queue.append(neighbor)
                        component.append(neighbor)
        if len(component) >= _MIN_COMPONENT_AREA:
            components.append(component)
    return components


def _round(value: float) -> float:
    return round(value, 6)


def _spot_from_component(
    component: list[tuple[int, int]],
    residual: FloatImage,
    frame_residuals: FloatImage,
    threshold: float,
    width: int,
    height: int,
) -> Spot | None:
    coordinates = np.asarray(component, dtype=np.int32)
    ys = coordinates[:, 0]
    xs = coordinates[:, 1]
    weights = residual[ys, xs].astype(np.float64)
    total_weight = float(np.sum(weights))
    center_x = float(np.sum(xs * weights) / total_weight)
    center_y = float(np.sum(ys * weights) / total_weight)
    sample_x = min(width - 1, max(0, round(center_x)))
    sample_y = min(height - 1, max(0, round(center_y)))
    persistence = float(np.mean(frame_residuals[:, sample_y, sample_x] >= threshold * 0.75))
    if persistence < _MIN_PERSISTENCE:
        return None

    image_x = center_x / max(1, width - 1)
    image_y = center_y / max(1, height - 1)
    return Spot(
        spot_id=0,
        image_x=_round(image_x),
        image_y=_round(image_y),
        sensor_x=_round(1.0 - image_x),
        sensor_y=_round(1.0 - image_y),
        bbox_left=_round(float(np.min(xs)) / max(1, width - 1)),
        bbox_top=_round(float(np.min(ys)) / max(1, height - 1)),
        bbox_right=_round(float(np.max(xs)) / max(1, width - 1)),
        bbox_bottom=_round(float(np.max(ys)) / max(1, height - 1)),
        area_pixels=len(component),
        mean_contrast=_round(float(np.mean(weights))),
        peak_contrast=_round(float(np.max(weights))),
        persistence=_round(persistence),
    )


def analyze_session(session: ImageSession, *, sensitivity: float = 4.0) -> DetectionResult:
    """Find dark residual components that persist across a validated session."""
    frame_residuals = np.stack([_residual_for(frame) for frame in session.frames])
    median_residual = np.median(frame_residuals, axis=0).astype(np.float32)
    threshold = _threshold(median_residual, sensitivity)
    mask = median_residual >= threshold
    mask_fraction = float(np.mean(mask))
    if mask_fraction > 0.10:
        raise CaptureQualityError(
            f"residual mask covers {mask_fraction:.1%} of the image; use a smoother flat field"
        )

    spots = [
        spot
        for component in _components(mask)
        if (
            spot := _spot_from_component(
                component,
                median_residual,
                frame_residuals,
                threshold,
                session.analysis_width,
                session.analysis_height,
            )
        )
        is not None
    ]
    spots.sort(key=lambda spot: (spot.image_y, spot.image_x))
    numbered = tuple(replace(spot, spot_id=index) for index, spot in enumerate(spots, start=1))
    median_frame = np.rint(np.median(session.frames, axis=0) * 255).astype(np.uint8)
    return DetectionResult(
        session=session,
        threshold=_round(threshold),
        spots=numbered,
        median_frame=median_frame,
        residual_map=median_residual,
    )
