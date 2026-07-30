"""Released and digitized moments used by the curated example."""

from __future__ import annotations

import csv
from pathlib import Path

HORIZONS = list(range(21))

# Central point estimates digitized from the published Figure 3 lines.
WITHIN_NEG_DIVERSE = [
    -0.297, -0.544, -0.556, -0.574, -0.427, -0.534, -0.447,
    -0.451, -0.415, -0.455, -0.512, -0.457, -0.485, -0.475,
    -0.443, -0.459, -0.524, -0.566, -0.504, -0.528, -0.492,
]
WITHIN_NEG_CONCENTRATED = [
    -0.544, -0.856, -0.874, -0.878, -0.718, -0.811, -0.680,
    -0.631, -0.386, -0.609, -0.750, -0.591, -0.477, -0.530,
    -0.485, -0.496, -0.682, -0.708, -0.603, -0.643, -0.748,
]
SPATIAL_NEG_DIVERSE = [
    0.183, 0.063, 0.023, -0.297, -0.266, -0.457, -0.419,
    -0.520, -0.426, -0.338, -0.419, -0.579, -0.429, -0.495,
    -0.505, -0.574, -0.685, -0.723, -0.698, -0.845, -0.931,
]
SPATIAL_NEG_CONCENTRATED = [
    0.185, 0.051, 0.061, -0.482, -0.579, -0.799, -0.756,
    -0.825, -0.381, -0.452, -0.561, -0.779, -0.406, -0.668,
    -0.721, -0.784, -1.132, -1.132, -1.114, -1.338, -1.571,
]

NEGATIVE_WELFARE = (
    ("more diversified · HHI decile 1", "#7EB28A", (-1.00, -0.06, -1.06)),
    ("more concentrated · HHI decile 10", "#D8904B", (-2.38, -2.55, -4.93)),
)
POSITIVE_WELFARE = (
    ("more diversified · HHI decile 1", "#7EB28A", (7.10, -3.25, 3.85)),
    ("more concentrated · HHI decile 10", "#D8904B", (12.75, -6.94, 5.81)),
)


def released_shocks() -> list[dict[str, str]]:
    path = Path(__file__).with_name("data") / "bartik_selected.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
