from __future__ import annotations

import json
from pathlib import Path

import pytest

from sensorsieve.cli import main
from sensorsieve.compare import compare_results
from sensorsieve.detect import analyze_session
from sensorsieve.errors import InputError
from sensorsieve.images import load_session
from sensorsieve.model import DetectionResult
from tests.helpers import three_frames, write_flat_session


def _analysis(root: Path, *spots: tuple[float, float, float, float]) -> DetectionResult:
    session = write_flat_session(root, frame_spots=three_frames(*spots))
    return analyze_session(load_session(session))


def test_compare_classifies_resolved_persistent_and_new(tmp_path: Path) -> None:
    before = _analysis(
        tmp_path / "before",
        (42.0, 38.0, 5.0, 72.0),
        (112.0, 78.0, 5.0, 70.0),
    )
    after = _analysis(
        tmp_path / "after",
        (113.0, 78.0, 5.0, 70.0),
        (138.0, 28.0, 4.5, 74.0),
    )

    comparison = compare_results(before, after)

    assert [spot.spot_id for spot in comparison.resolved] == [1]
    assert len(comparison.persistent) == 1
    assert comparison.persistent[0].before.spot_id == 2
    assert comparison.persistent[0].after.spot_id == 2
    assert comparison.persistent[0].distance < 0.01
    assert [spot.spot_id for spot in comparison.new] == [1]


def test_compare_rejects_different_capture_dimensions(tmp_path: Path) -> None:
    before = _analysis(tmp_path / "before", (42.0, 38.0, 5.0, 72.0))
    after_dir = write_flat_session(
        tmp_path / "after",
        frame_spots=three_frames((84.0, 76.0, 10.0, 72.0)),
        size=(320, 240),
    )
    after = analyze_session(load_session(after_dir))

    with pytest.raises(InputError, match="matching original dimensions"):
        compare_results(before, after)


def test_compare_match_radius_is_fraction_of_image_diagonal(tmp_path: Path) -> None:
    before = _analysis(tmp_path / "before", (80.0, 60.0, 5.0, 72.0))
    after = _analysis(tmp_path / "after", (84.0, 60.0, 5.0, 72.0))

    comparison = compare_results(before, after)

    assert len(comparison.persistent) == 1
    assert comparison.resolved == ()
    assert comparison.new == ()


def test_compare_cli_writes_artifacts_and_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before_dir = write_flat_session(
        tmp_path / "before",
        frame_spots=three_frames((42.0, 38.0, 5.0, 72.0), (112.0, 78.0, 5.0, 70.0)),
    )
    after_dir = write_flat_session(
        tmp_path / "after",
        frame_spots=three_frames((113.0, 78.0, 5.0, 70.0), (138.0, 28.0, 4.5, 74.0)),
    )
    output_dir = tmp_path / "comparison"

    exit_code = main(
        [
            "compare",
            str(before_dir),
            str(after_dir),
            "--output",
            str(output_dir),
        ]
    )

    assert exit_code == 1
    assert {path.name for path in output_dir.iterdir()} == {
        "after-overlay.png",
        "before-overlay.png",
        "changes.csv",
        "report.json",
        "summary.txt",
    }
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert report["schema_version"] == 1
    assert report["kind"] == "comparison"
    assert report["status"] == "review"
    assert len(report["resolved"]) == 1
    assert len(report["persistent"]) == 1
    assert len(report["new"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "review: 1 persistent, 1 new, 1 resolved; artifacts written\n"
    assert captured.err == ""


def test_compare_with_only_resolved_spots_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before_dir = write_flat_session(
        tmp_path / "before", frame_spots=three_frames((42.0, 38.0, 5.0, 72.0))
    )
    after_dir = write_flat_session(tmp_path / "after", frame_spots=three_frames())

    exit_code = main(
        [
            "compare",
            str(before_dir),
            str(after_dir),
            "--output",
            str(tmp_path / "comparison"),
        ]
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == "clean: 0 persistent, 0 new, 1 resolved; artifacts written\n"
