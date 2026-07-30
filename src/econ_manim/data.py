"""Small, dependency-free readers for project-local animation data."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

from .config import ConfigError


def read_csv_rows(
    path: str | Path,
    *,
    required_columns: Sequence[str] = (),
) -> tuple[dict[str, str], ...]:
    """Read a local CSV and fail with a concise message when its shape is wrong."""

    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = tuple(reader.fieldnames or ())
            missing = [column for column in required_columns if column not in columns]
            if missing:
                raise ConfigError(
                    f"{source} is missing CSV columns: {', '.join(missing)}"
                )
            rows = tuple(dict(row) for row in reader)
    except FileNotFoundError as error:
        raise ConfigError(f"missing local data file: {source}") from error
    if not rows:
        raise ConfigError(f"local data file has no rows: {source}")
    return rows
