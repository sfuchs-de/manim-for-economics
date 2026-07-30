"""Load the released and digitized moments bundled with the case study."""

from __future__ import annotations

import csv
from pathlib import Path

DATA_DIR = Path(__file__).with_name("data")


def _rows(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


_figure3 = _rows("figure3_point_estimates.csv")
HORIZONS = [int(row["horizon"]) for row in _figure3]
WITHIN_NEG_DIVERSE = [float(row["within_lower_hhi"]) for row in _figure3]
WITHIN_NEG_CONCENTRATED = [float(row["within_higher_hhi"]) for row in _figure3]
SPATIAL_NEG_DIVERSE = [float(row["spatial_lower_hhi"]) for row in _figure3]
SPATIAL_NEG_CONCENTRATED = [float(row["spatial_higher_hhi"]) for row in _figure3]


def welfare_rows(theme, shock_group: str):
    """Return one welfare table with colors supplied by the active visual theme."""

    rows = []
    colors = {
        "more diversified · HHI decile 1": theme.green,
        "more concentrated · HHI decile 10": theme.orange,
    }
    for row in _rows("table2_welfare.csv"):
        if row["shock_group"] != shock_group:
            continue
        label = row["hhi_group"]
        values = tuple(
            float(row[field])
            for field in ("direct_effect", "second_order", "total")
        )
        rows.append((label, colors[label], values))
    if not rows:
        raise ValueError(f"unknown welfare shock group: {shock_group}")
    return tuple(rows)


def released_shocks() -> list[dict[str, str]]:
    return _rows("bartik_selected.csv")
