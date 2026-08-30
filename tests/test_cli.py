from __future__ import annotations

import subprocess
import sys


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
