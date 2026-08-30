from __future__ import annotations

import runpy
import subprocess
import sys

import pytest

from sensorsieve.cli import main


def test_module_reports_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "sensorsieve", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == "sensorsieve 0.1.0\n"
    assert result.stderr == ""


def test_module_entrypoint_exits_after_reporting_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["sensorsieve", "--version"])

    with pytest.raises(SystemExit) as raised:
        runpy.run_module("sensorsieve", run_name="__main__")

    assert raised.value.code == 0
    assert capsys.readouterr().out == "sensorsieve 0.1.0\n"


@pytest.mark.parametrize(
    ("option", "value"),
    [("--sensitivity", "1.9"), ("--max-side", "511")],
)
def test_cli_rejects_out_of_range_analysis_options(option: str, value: str) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["inspect", "unused", "--output", "unused-output", option, value])

    assert raised.value.code == 2
