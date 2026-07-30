import pytest

from econ_manim.cli import build_parser, main
from econ_manim.config import load_project, validate_data_manifest


def test_cli_exposes_planned_commands():
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {
        "doctor",
        "templates",
        "new",
        "preview",
        "render",
        "frames",
        "qa",
        "audio",
    }


def test_qa_accepts_starter_without_render():
    assert main(["qa", "starter"]) == 0


def test_new_copies_a_renderable_project(tmp_path):
    assert main(["new", "research-paper", "--destination", str(tmp_path)]) == 0
    project = load_project(tmp_path / "research-paper")
    assert project.title == "Research Paper"
    assert project.output_file == "research_paper"


@pytest.mark.parametrize(
    ("template", "scene"),
    (
        ("general", "PaperExplainer"),
        ("mechanism-led", "MechanismExplainer"),
        ("agent-choice-welfare", "ChoiceWelfareExplainer"),
    ),
)
def test_new_supports_each_project_template(tmp_path, template, scene):
    name = f"{template}-paper"
    assert (
        main(
            [
                "new",
                name,
                "--template",
                template,
                "--destination",
                str(tmp_path),
            ]
        )
        == 0
    )
    project = load_project(tmp_path / name)
    assert project.scene == scene
    assert validate_data_manifest(tmp_path / name)
    assert not (tmp_path / name / "preview").exists()


def test_templates_explains_narrative_grammars(capsys):
    assert main(["templates"]) == 0
    output = capsys.readouterr().out
    assert "mechanism-led" in output
    assert "multimodal-transport explainer" in output
    assert "agent-choice-welfare" in output
    assert "economic-diversity explainer" in output


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
