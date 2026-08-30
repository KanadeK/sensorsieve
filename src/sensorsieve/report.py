from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from sensorsieve.errors import OutputError
from sensorsieve.model import DetectionResult, Spot

_INSPECTION_FILES = ("report.json", "spots.csv", "overlay.png", "summary.txt")
_SPOT_FIELDS = (
    "spot_id",
    "image_x",
    "image_y",
    "sensor_x",
    "sensor_y",
    "bbox_left",
    "bbox_top",
    "bbox_right",
    "bbox_bottom",
    "area_pixels",
    "mean_contrast",
    "peak_contrast",
    "persistence",
)


def assert_output_available(output_dir: Path) -> None:
    """Validate an output boundary without creating or deleting anything."""
    if output_dir.is_symlink():
        raise OutputError("output directory cannot be a symbolic link")
    if output_dir.exists():
        if not output_dir.is_dir():
            raise OutputError("output path must be a directory")
        if any(output_dir.iterdir()):
            raise OutputError("output directory must be empty")
    elif not output_dir.parent.is_dir():
        raise OutputError("output parent directory must already exist")


def _spot_dict(spot: Spot) -> dict[str, int | float]:
    return {
        "spot_id": spot.spot_id,
        "image_x": spot.image_x,
        "image_y": spot.image_y,
        "sensor_x": spot.sensor_x,
        "sensor_y": spot.sensor_y,
        "bbox_left": spot.bbox_left,
        "bbox_top": spot.bbox_top,
        "bbox_right": spot.bbox_right,
        "bbox_bottom": spot.bbox_bottom,
        "area_pixels": spot.area_pixels,
        "mean_contrast": spot.mean_contrast,
        "peak_contrast": spot.peak_contrast,
        "persistence": spot.persistence,
    }


def inspection_payload(result: DetectionResult) -> dict[str, Any]:
    session = result.session
    return {
        "schema_version": 1,
        "kind": "inspection",
        "status": "review" if result.spots else "clean",
        "source": {
            "file_count": len(session.filenames),
            "original_size": {
                "width": session.original_width,
                "height": session.original_height,
            },
            "analysis_size": {
                "width": session.analysis_width,
                "height": session.analysis_height,
            },
        },
        "method": {
            "threshold": result.threshold,
            "minimum_frame_persistence": round(2 / 3, 6),
        },
        "spots": [_spot_dict(spot) for spot in result.spots],
        "limitations": [
            "Persistent dark features are candidates, not proof of sensor dust.",
            "Mirrored sensor guidance may depend on camera orientation.",
            "SensorSieve does not recommend or perform cleaning.",
        ],
    }


def _spots_csv(spots: tuple[Spot, ...]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=_SPOT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(_spot_dict(spot) for spot in spots)
    return stream.getvalue()


def _overlay_bytes(result: DetectionResult) -> bytes:
    image = Image.fromarray(result.median_frame, mode="L").convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for spot in result.spots:
        left = round(spot.bbox_left * (width - 1))
        top = round(spot.bbox_top * (height - 1))
        right = round(spot.bbox_right * (width - 1))
        bottom = round(spot.bbox_bottom * (height - 1))
        center_x = round(spot.image_x * (width - 1))
        center_y = round(spot.image_y * (height - 1))
        draw.rectangle((left - 2, top - 2, right + 2, bottom + 2), outline=(220, 32, 32), width=2)
        draw.line((center_x - 4, center_y, center_x + 4, center_y), fill=(255, 220, 0))
        draw.line((center_x, center_y - 4, center_x, center_y + 4), fill=(255, 220, 0))
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=False)
    return stream.getvalue()


def _summary(result: DetectionResult) -> str:
    session = result.session
    status = "REVIEW" if result.spots else "CLEAN"
    return (
        "SensorSieve inspection\n"
        f"Status: {status}\n"
        f"Frames: {len(session.filenames)}\n"
        f"Original size: {session.original_width}x{session.original_height}\n"
        f"Analysis size: {session.analysis_width}x{session.analysis_height}\n"
        f"Threshold: {result.threshold:.6f}\n"
        f"Persistent spots: {len(result.spots)}\n"
        f"Exit code: {1 if result.spots else 0}\n"
    )


def write_inspection(result: DetectionResult, output_dir: Path) -> None:
    """Write the complete inspection artifact set into an available directory."""
    payloads = {
        "report.json": (
            json.dumps(inspection_payload(result), indent=2, sort_keys=True) + "\n"
        ).encode(),
        "spots.csv": _spots_csv(result.spots).encode(),
        "overlay.png": _overlay_bytes(result),
        "summary.txt": _summary(result).encode(),
    }
    try:
        output_dir.mkdir(exist_ok=True)
        for filename in _INSPECTION_FILES:
            (output_dir / filename).write_bytes(payloads[filename])
    except OSError as error:
        raise OutputError(
            f"cannot write inspection artifacts: {error.strerror or error}"
        ) from error
