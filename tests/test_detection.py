from __future__ import annotations

from pathlib import Path

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
