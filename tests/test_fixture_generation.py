from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

import scripts.build_examples as build_examples


def test_fixture_bytes_ignore_one_ulp_transcendental_difference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build_examples, "EXAMPLES", tmp_path)
    frames = (((80.0, 120.0, 8.0, 76.0),),) * 3
    build_examples._write_session("baseline", frames)
    original_exp = np.exp

    def shifted_exp(values: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.asarray(np.nextafter(original_exp(values), np.inf), dtype=np.float64)

    monkeypatch.setattr(np, "exp", shifted_exp)
    build_examples._write_session("one-ulp", frames)

    for index in range(1, 4):
        filename = f"flat-{index}.png"
        assert (tmp_path / "baseline" / filename).read_bytes() == (
            tmp_path / "one-ulp" / filename
        ).read_bytes()
