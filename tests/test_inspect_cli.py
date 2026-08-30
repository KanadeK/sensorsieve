from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from PIL import Image

from sensorsieve.cli import main
from tests.helpers import three_frames, write_flat_session


def test_inspect_writes_review_artifacts_and_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    session_dir = write_flat_session(
        tmp_path / "dirty",
        frame_spots=three_frames((104.0, 42.0, 5.0, 72.0)),
    )
    output_dir = tmp_path / "report"

    exit_code = main(["inspect", str(session_dir), "--output", str(output_dir)])

    assert exit_code == 1
    assert {path.name for path in output_dir.iterdir()} == {
        "overlay.png",
        "report.json",
        "spots.csv",
        "summary.txt",
    }
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert report["schema_version"] == 1
    assert report["kind"] == "inspection"
    assert report["status"] == "review"
    assert report["source"] == {
        "analysis_size": {"height": 120, "width": 160},
        "file_count": 3,
        "original_size": {"height": 120, "width": 160},
    }
    assert len(report["spots"]) == 1
    assert "D:" not in (output_dir / "report.json").read_text(encoding="utf-8")
    csv_lines = (output_dir / "spots.csv").read_text(encoding="utf-8").splitlines()
    assert csv_lines[0].startswith("spot_id,image_x,image_y,sensor_x,sensor_y")
    assert len(csv_lines) == 2
    with Image.open(output_dir / "overlay.png") as overlay:
        assert overlay.size == (160, 120)
        assert overlay.mode == "RGB"
    captured = capsys.readouterr()
    assert captured.out == "review: 1 persistent spot; artifacts written\n"
    assert captured.err == ""


def test_inspect_clean_session_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    session_dir = write_flat_session(tmp_path / "clean", frame_spots=three_frames())

    exit_code = main(["inspect", str(session_dir), "--output", str(tmp_path / "clean-report")])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == "clean: no persistent spots; artifacts written\n"
    assert captured.err == ""


def test_inspect_invalid_input_returns_two_without_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "invalid-report"

    exit_code = main(["inspect", str(tmp_path / "missing"), "--output", str(output_dir)])

    assert exit_code == 2
    assert not output_dir.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "sensorsieve: error: input must be a real directory\n"


def test_inspect_refuses_nonempty_output_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    session_dir = write_flat_session(tmp_path / "clean", frame_spots=three_frames())
    output_dir = tmp_path / "report"
    output_dir.mkdir()
    sentinel = output_dir / "keep.txt"
    sentinel.write_text("owner data", encoding="utf-8")

    exit_code = main(["inspect", str(session_dir), "--output", str(output_dir)])

    assert exit_code == 2
    assert sentinel.read_text(encoding="utf-8") == "owner data"
    captured = capsys.readouterr()
    assert captured.err == "sensorsieve: error: output directory must be empty\n"


def test_inspect_refuses_output_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    session_dir = write_flat_session(tmp_path / "clean", frame_spots=three_frames())
    output_file = tmp_path / "report.txt"
    output_file.write_text("owner data", encoding="utf-8")

    assert main(["inspect", str(session_dir), "--output", str(output_file)]) == 2
    assert output_file.read_text(encoding="utf-8") == "owner data"
    assert "output path must be a directory" in capsys.readouterr().err


def test_inspect_requires_existing_output_parent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    session_dir = write_flat_session(tmp_path / "clean", frame_spots=three_frames())
    output_dir = tmp_path / "missing-parent" / "report"

    assert main(["inspect", str(session_dir), "--output", str(output_dir)]) == 2
    assert not output_dir.exists()
    assert "output parent directory must already exist" in capsys.readouterr().err


def test_inspect_converts_directory_permission_error_to_exit_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    session_dir = write_flat_session(tmp_path / "session", frame_spots=three_frames())
    original_iterdir = Path.iterdir

    def denied_iterdir(path: Path) -> Iterator[Path]:
        if path == session_dir:
            raise PermissionError("denied for test")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", denied_iterdir)

    exit_code = main(["inspect", str(session_dir), "--output", str(tmp_path / "output")])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "sensorsieve: error: cannot read input directory\n"
