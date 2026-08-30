from __future__ import annotations

from math import hypot

from sensorsieve.errors import InputError
from sensorsieve.model import ComparisonResult, DetectionResult, Spot, SpotMatch


def compare_results(
    before: DetectionResult,
    after: DetectionResult,
    *,
    maximum_distance: float = 0.025,
) -> ComparisonResult:
    """Match spots one-to-one by deterministic nearest normalized position."""
    before_size = (before.session.original_width, before.session.original_height)
    after_size = (after.session.original_width, after.session.original_height)
    if before_size != after_size:
        raise InputError("comparison sessions must have matching original dimensions")

    candidates: list[tuple[float, int, int, Spot, Spot]] = []
    for before_spot in before.spots:
        for after_spot in after.spots:
            width = max(1, before.session.original_width - 1)
            height = max(1, before.session.original_height - 1)
            diagonal = hypot(width, height)
            distance = (
                hypot(
                    (before_spot.image_x - after_spot.image_x) * width,
                    (before_spot.image_y - after_spot.image_y) * height,
                )
                / diagonal
            )
            if distance <= maximum_distance:
                candidates.append(
                    (distance, before_spot.spot_id, after_spot.spot_id, before_spot, after_spot)
                )
    candidates.sort(key=lambda candidate: candidate[:3])

    used_before: set[int] = set()
    used_after: set[int] = set()
    persistent: list[SpotMatch] = []
    for distance, before_id, after_id, before_spot, after_spot in candidates:
        if before_id in used_before or after_id in used_after:
            continue
        used_before.add(before_id)
        used_after.add(after_id)
        persistent.append(
            SpotMatch(before=before_spot, after=after_spot, distance=round(distance, 6))
        )

    persistent.sort(key=lambda match: match.before.spot_id)
    resolved = tuple(spot for spot in before.spots if spot.spot_id not in used_before)
    new = tuple(spot for spot in after.spots if spot.spot_id not in used_after)
    return ComparisonResult(
        before=before,
        after=after,
        resolved=resolved,
        persistent=tuple(persistent),
        new=new,
    )
