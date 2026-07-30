import pytest

from econ_manim.cli import build_parser, main
from econ_manim.config import load_project


def test_cli_exposes_planned_commands():
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {"doctor", "new", "preview", "render", "frames", "qa", "audio"}


def test_qa_accepts_starter_without_render():
    assert main(["qa", "starter"]) == 0


def test_new_copies_a_renderable_project(tmp_path):
    assert main(["new", "labor-paper", "--destination", str(tmp_path)]) == 0
    project = load_project(tmp_path / "labor-paper")
    assert project.title == "Labor Paper"
    assert project.output_file == "labor_paper"


def test_missing_project_reports_a_concise_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["qa", str(tmp_path / "missing")])
    assert exit_info.value.code == 2
    assert "missing configuration" in capsys.readouterr().err


def test_audio_requires_an_explicit_configuration(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["audio", "starter"])
    assert exit_info.value.code == 2
    assert "audio.enabled is false" in capsys.readouterr().err
