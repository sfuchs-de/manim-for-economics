import pytest

from econ_manim.config import ConfigError
from econ_manim.data import read_csv_rows


def test_read_csv_rows_validates_and_returns_local_records(tmp_path):
    source = tmp_path / "values.csv"
    source.write_text("label,value\nA,1\nB,2\n", encoding="utf-8")
    rows = read_csv_rows(source, required_columns=("label", "value"))
    assert rows == (
        {"label": "A", "value": "1"},
        {"label": "B", "value": "2"},
    )


def test_read_csv_rows_rejects_missing_columns(tmp_path):
    source = tmp_path / "values.csv"
    source.write_text("label\nA\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="missing CSV columns: value"):
        read_csv_rows(source, required_columns=("label", "value"))


def test_read_csv_rows_rejects_empty_data(tmp_path):
    source = tmp_path / "values.csv"
    source.write_text("label,value\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="has no rows"):
        read_csv_rows(source)
