from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from sensorsieve.detect import analyze_session
from sensorsieve.errors import CaptureQualityError, InputError
from sensorsieve.images import load_session
from tests.helpers import three_frames, write_flat_session


def test_detects_persistent_spot_but_not_one_frame_mark(tmp_path: Path) -> None:
    persistent = (104.0, 42.0, 5.0, 72.0)
    transient = (32.0, 84.0, 5.0, 80.0)
    frames = (
        (persistent, transient),
        (persistent,),
        (persistent,),
    )
    session = load_session(write_flat_session(tmp_path / "session", frame_spots=frames))

    result = analyze_session(session, sensitivity=4.0)

    assert len(result.spots) == 1
    spot = result.spots[0]
    assert spot.image_x == pytest.approx(104 / 159, abs=0.03)
    assert spot.image_y == pytest.approx(42 / 119, abs=0.03)
    assert spot.sensor_x == pytest.approx(1.0 - spot.image_x)
    assert spot.sensor_y == pytest.approx(1.0 - spot.image_y)
    assert spot.persistence == pytest.approx(1.0)
    assert spot.peak_contrast > spot.mean_contrast > 0.01


def test_clean_gradient_has_no_spots(tmp_path: Path) -> None:
    session = load_session(write_flat_session(tmp_path / "clean", frame_spots=three_frames()))

    result = analyze_session(session, sensitivity=4.0)

    assert result.spots == ()


def test_load_session_rejects_fewer_than_three_frames(tmp_path: Path) -> None:
    session_dir = write_flat_session(tmp_path / "short", frame_spots=((), ()))

    with pytest.raises(InputError, match="at least 3"):
        load_session(session_dir)


def test_load_session_rejects_mixed_dimensions(tmp_path: Path) -> None:
    session_dir = write_flat_session(
        tmp_path / "mixed", frame_spots=three_frames(), size=(160, 120)
    )
    Image.new("L", (100, 80), 190).save(session_dir / "flat-3.png")

    with pytest.raises(InputError, match="matching dimensions"):
        load_session(session_dir)


def test_load_session_rejects_forged_extension(tmp_path: Path) -> None:
    session_dir = write_flat_session(tmp_path / "forged", frame_spots=three_frames())
    (session_dir / "flat-3.png").write_text("not an image", encoding="utf-8")

    with pytest.raises(InputError, match="cannot decode"):
        load_session(session_dir)


def test_load_session_rejects_dark_capture(tmp_path: Path) -> None:
    session_dir = write_flat_session(tmp_path / "dark", frame_spots=three_frames(), brightness=10.0)

    with pytest.raises(CaptureQualityError, match="mean luminance"):
        load_session(session_dir)


def test_load_session_rejects_non_directory(tmp_path: Path) -> None:
    input_file = tmp_path / "flat.png"
    Image.new("L", (32, 32), 190).save(input_file)

    with pytest.raises(InputError, match="directory"):
        load_session(input_file)


def test_load_session_rejects_too_many_images(tmp_path: Path) -> None:
    session_dir = tmp_path / "too-many"
    session_dir.mkdir()
    for index in range(33):
        (session_dir / f"flat-{index:02}.png").write_bytes(b"not decoded")

    with pytest.raises(InputError, match="more than 32"):
        load_session(session_dir)


def test_load_session_rejects_mislabelled_format(tmp_path: Path) -> None:
    session_dir = tmp_path / "mislabelled"
    session_dir.mkdir()
    for index in range(3):
        Image.new("L", (64, 64), 190).save(session_dir / f"flat-{index}.png", format="BMP")

    with pytest.raises(InputError, match="unsupported encoded image format"):
        load_session(session_dir)


def test_load_session_rejects_clipped_capture(tmp_path: Path) -> None:
    session_dir = tmp_path / "clipped"
    session_dir.mkdir()
    pixels = np.full((120, 160), 180, dtype=np.uint8)
    pixels[:, :40] = 255
    for index in range(3):
        Image.fromarray(pixels, mode="L").save(session_dir / f"flat-{index}.png")

    with pytest.raises(CaptureQualityError, match="clipped pixels"):
        load_session(session_dir)


def test_load_session_rejects_out_of_range_max_side(tmp_path: Path) -> None:
    session_dir = write_flat_session(tmp_path / "session", frame_spots=three_frames())

    with pytest.raises(InputError, match="max-side"):
        load_session(session_dir, max_side=511)


def test_detection_excludes_feature_below_required_persistence(tmp_path: Path) -> None:
    feature = (104.0, 42.0, 5.0, 72.0)
    session_dir = write_flat_session(
        tmp_path / "intermittent",
        frame_spots=((feature,), (feature,), (), ()),
    )

    result = analyze_session(load_session(session_dir))

    assert result.spots == ()


def test_detection_rejects_texture_dominated_field(tmp_path: Path) -> None:
    session_dir = tmp_path / "textured"
    session_dir.mkdir()
    y, x = np.mgrid[0:120, 0:160]
    dot_distance = ((x % 16) - 8) ** 2 + ((y % 16) - 8) ** 2
    pixels = np.where(dot_distance <= 4**2, 135, 205).astype(np.uint8)
    for index in range(3):
        Image.fromarray(pixels, mode="L").save(session_dir / f"flat-{index}.png")

    with pytest.raises(CaptureQualityError, match="residual mask covers"):
        analyze_session(load_session(session_dir))
