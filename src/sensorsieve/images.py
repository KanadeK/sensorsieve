from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from sensorsieve.errors import CaptureQualityError, InputError
from sensorsieve.model import FloatImage, ImageSession

_EXTENSIONS = {".jpg", ".jpeg", ".png"}
_FORMATS = {"JPEG", "PNG"}
_MIN_FILES = 3
_MAX_FILES = 32
_MAX_FILE_BYTES = 100 * 1024 * 1024
_MAX_ANALYSIS_PIXELS = 96_000_000


def _candidate_files(input_dir: Path) -> tuple[Path, ...]:
    if not input_dir.is_dir() or input_dir.is_symlink():
        raise InputError("input must be a real directory")

    candidates: list[Path] = []
    for entry in input_dir.iterdir():
        if entry.suffix.lower() not in _EXTENSIONS:
            continue
        if entry.is_symlink():
            raise InputError(f"symbolic-link image is not allowed: {entry.name}")
        if entry.is_file():
            candidates.append(entry)

    paths = tuple(sorted(candidates, key=lambda path: (path.name.casefold(), path.name)))
    if len(paths) < _MIN_FILES:
        raise InputError("input directory must contain at least 3 JPEG or PNG files")
    if len(paths) > _MAX_FILES:
        raise InputError(f"input directory contains more than {_MAX_FILES} supported images")
    return paths


def _decode_grayscale(path: Path, max_side: int) -> tuple[FloatImage, tuple[int, int]]:
    if path.stat().st_size > _MAX_FILE_BYTES:
        raise InputError(f"image exceeds the 100 MiB limit: {path.name}")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as probe:
                if probe.format not in _FORMATS:
                    raise InputError(f"unsupported encoded image format: {path.name}")
                probe.verify()
            with Image.open(path) as source:
                oriented = ImageOps.exif_transpose(source)
                grayscale = oriented.convert("L")
                original_size = grayscale.size
                if max(original_size) > max_side:
                    scale = max_side / max(original_size)
                    resized = (
                        max(1, round(original_size[0] * scale)),
                        max(1, round(original_size[1] * scale)),
                    )
                    grayscale = grayscale.resize(resized, Image.Resampling.LANCZOS)
                pixels = np.asarray(grayscale, dtype=np.float32) / np.float32(255.0)
    except InputError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise InputError(f"image exceeds Pillow safety limits: {path.name}") from error
    except (OSError, SyntaxError, UnidentifiedImageError, ValueError) as error:
        raise InputError(f"cannot decode JPEG or PNG image: {path.name}") from error

    return pixels, original_size


def _validate_capture(pixels: FloatImage, filename: str) -> None:
    mean = float(np.mean(pixels, dtype=np.float64))
    if not 0.15 <= mean <= 0.95:
        raise CaptureQualityError(
            f"mean luminance for {filename} must be between 15% and 95%; got {mean:.1%}"
        )
    clipped = float(np.mean((pixels <= 1 / 255) | (pixels >= 254 / 255)))
    if clipped > 0.10:
        raise CaptureQualityError(f"clipped pixels for {filename} exceed 10%; got {clipped:.1%}")


def load_session(input_dir: Path, *, max_side: int = 2048) -> ImageSession:
    """Decode and validate one bounded, non-recursive flat-field session."""
    if not 512 <= max_side <= 8192:
        raise InputError("max-side must be between 512 and 8192")

    paths = _candidate_files(input_dir)
    decoded: list[FloatImage] = []
    original_size: tuple[int, int] | None = None
    analysis_size: tuple[int, int] | None = None
    for path in paths:
        pixels, current_original = _decode_grayscale(path, max_side)
        current_analysis = (pixels.shape[1], pixels.shape[0])
        if original_size is None:
            original_size = current_original
            analysis_size = current_analysis
        elif current_original != original_size or current_analysis != analysis_size:
            raise InputError("all images in a session must have matching dimensions")
        _validate_capture(pixels, path.name)
        decoded.append(pixels)

    assert original_size is not None and analysis_size is not None
    total_analysis_pixels = analysis_size[0] * analysis_size[1] * len(decoded)
    if total_analysis_pixels > _MAX_ANALYSIS_PIXELS:
        raise InputError("analysis would exceed the 96 million pixel session limit")

    return ImageSession(
        filenames=tuple(path.name for path in paths),
        original_width=original_size[0],
        original_height=original_size[1],
        analysis_width=analysis_size[0],
        analysis_height=analysis_size[1],
        frames=np.stack(decoded).astype(np.float32, copy=False),
    )
