from pathlib import Path

import pytest

from econ_manim.config import (
    ConfigError,
    load_data_manifest,
    load_project,
    validate_data_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_starter_project_loads():
    project = load_project(ROOT / "starter")
    assert project.scene == "PaperExplainer"
    assert project.theme == "midnight"
    assert project.render.preview_width == 854
    assert project.render.fps == 30
    assert project.render.inspection_frames
    assert {frame.kind for frame in project.render.inspection_frames} == {
        "settled",
        "transition",
    }
    assert project.audio.enabled is False


def test_general_starter_does_not_assume_a_labor_market_paper():
    starter = ROOT / "starter"
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in starter.rglob("*")
        if path.is_file() and path.suffix in {".py", ".md", ".toml", ".csv"}
    ).lower()
    for labor_specific_term in ("worker", "labor market", "city a", "bartik", "hhi"):
        assert labor_specific_term not in text


def test_case_study_manifest_is_explicit_and_valid():
    entries = load_data_manifest(ROOT / "examples" / "economic_diversity")
    assert {entry.status for entry in entries} == {"released", "digitized"}
    assert {entry.classification for entry in entries} == {"actual"}
    assert all(entry.transformation and entry.displayed_values for entry in entries)
    messages = validate_data_manifest(ROOT / "examples" / "economic_diversity")
    assert any("released-bartik-selected-cities" in message for message in messages)


def test_manifest_rejects_unknown_status(tmp_path):
    (tmp_path / "data_manifest.toml").write_text(
        '[[dataset]]\nid="bad"\nstatus="probably-real"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="invalid status"):
        load_data_manifest(tmp_path)


def test_manifest_rejects_missing_displayed_values(tmp_path):
    (tmp_path / "data_manifest.toml").write_text(
        """
[[dataset]]
id = "incomplete"
status = "illustrative"
classification = "illustrative"
transformation = "None"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="displayed_values"):
        load_data_manifest(tmp_path)


def test_manifest_requires_at_least_one_dataset(tmp_path):
    (tmp_path / "data_manifest.toml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigError, match="at least one"):
        load_data_manifest(tmp_path)


def test_project_rejects_missing_entrypoint(tmp_path):
    (tmp_path / "project.toml").write_text(
        """
[project]
title = "Missing"
entrypoint = "absent.py"
scene = "MissingScene"
output_file = "missing"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="entrypoint does not exist"):
        load_project(tmp_path)


def test_project_rejects_unknown_inspection_frame_kind(tmp_path):
    (tmp_path / "scenes.py").write_text("", encoding="utf-8")
    (tmp_path / "project.toml").write_text(
        """
[project]
title = "Bad frame"
entrypoint = "scenes.py"
scene = "Scene"
output_file = "bad"

[[qa.frame]]
time = 1.0
label = "not classified"
kind = "maybe"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="invalid kind"):
        load_project(tmp_path)


def test_project_rejects_unknown_theme(tmp_path):
    (tmp_path / "scenes.py").write_text("", encoding="utf-8")
    (tmp_path / "project.toml").write_text(
        """
[project]
title = "Bad theme"
entrypoint = "scenes.py"
scene = "Scene"
output_file = "bad"
theme = "chartreuse"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="unknown theme"):
        load_project(tmp_path)


def test_project_rejects_non_positive_render_configuration(tmp_path):
    (tmp_path / "scenes.py").write_text("", encoding="utf-8")
    (tmp_path / "project.toml").write_text(
        """
[project]
title = "Bad render"
entrypoint = "scenes.py"
scene = "Scene"
output_file = "bad"

[render]
preview_fps = 0
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="preview_fps"):
        load_project(tmp_path)
