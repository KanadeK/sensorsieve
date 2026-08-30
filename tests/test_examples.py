from __future__ import annotations

import json
from pathlib import Path

import pytest

from sensorsieve.cli import main

ROOT = Path(__file__).resolve().parent.parent


def test_committed_examples_cover_real_exit_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before_output = tmp_path / "before-output"
    assert (
        main(
            [
                "inspect",
                str(ROOT / "examples" / "before"),
                "--output",
                str(before_output),
            ]
        )
        == 1
    )
    before = json.loads((before_output / "report.json").read_text(encoding="utf-8"))
    assert len(before["spots"]) == 2

    clean_output = tmp_path / "clean-output"
    assert (
        main(
            [
                "inspect",
                str(ROOT / "examples" / "clean"),
                "--output",
                str(clean_output),
            ]
        )
        == 0
    )

    compare_output = tmp_path / "compare-output"
    assert (
        main(
            [
                "compare",
                str(ROOT / "examples" / "before"),
                str(ROOT / "examples" / "after"),
                "--output",
                str(compare_output),
            ]
        )
        == 1
    )
    comparison = json.loads((compare_output / "report.json").read_text(encoding="utf-8"))
    assert len(comparison["resolved"]) == 1
    assert len(comparison["persistent"]) == 1
    assert len(comparison["new"]) == 1

    assert (
        main(
            [
                "inspect",
                str(ROOT / "examples" / "invalid-too-few"),
                "--output",
                str(tmp_path / "invalid-output"),
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert "must contain at least 3" in captured.err
