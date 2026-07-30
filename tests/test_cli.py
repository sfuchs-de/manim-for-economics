import hashlib
from pathlib import Path

import pytest

import econ_manim.cli as cli
from econ_manim.cli import build_parser, main
from econ_manim.config import load_project, validate_data_manifest
from econ_manim.media import VideoInfo


def test_cli_exposes_planned_commands():
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {
        "doctor",
        "templates",
        "themes",
        "scenes",
        "preview-scene",
        "add-scene",
        "checksum",
        "demo",
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
    assert project.theme == "midnight"


@pytest.mark.parametrize(
    ("template", "scene", "default_theme"),
    (
        ("general", "PaperExplainer", "midnight"),
        ("mechanism-led", "MechanismExplainer", "ivory"),
        ("agent-choice-welfare", "ChoiceWelfareExplainer", "midnight"),
        ("empirical-result-led", "EmpiricalResultExplainer", "midnight"),
        ("method-theory", "MethodTheoryExplainer", "ivory"),
    ),
)
def test_new_supports_each_project_template(tmp_path, template, scene, default_theme):
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
    assert project.theme == default_theme
    assert validate_data_manifest(tmp_path / name)
    assert not (tmp_path / name / "preview").exists()


def test_new_keeps_theme_independent_from_narrative_template(tmp_path):
    assert (
        main(
            [
                "new",
                "light-choice-paper",
                "--template",
                "agent-choice-welfare",
                "--theme",
                "ivory",
                "--destination",
                str(tmp_path),
            ]
        )
        == 0
    )
    project = load_project(tmp_path / "light-choice-paper")
    assert project.scene == "ChoiceWelfareExplainer"
    assert project.theme == "ivory"


def test_templates_explains_narrative_grammars(capsys):
    assert main(["templates"]) == 0
    output = capsys.readouterr().out
    assert "mechanism-led" in output
    assert "multimodal-transport explainer" in output
    assert "agent-choice-welfare" in output
    assert "economic-diversity explainer" in output
    assert "Default theme: ivory" in output


def test_themes_explains_visual_presets(capsys):
    assert main(["themes"]) == 0
    output = capsys.readouterr().out
    assert "midnight" in output
    assert "Dark navy field" in output
    assert "ivory" in output
    assert "Warm paper field" in output


def test_scenes_lists_and_filters_atomic_recipes(capsys):
    assert main(["scenes", "--category", "empirical"]) == 0
    output = capsys.readouterr().out
    assert "empirical.coefficient-intervals" in output
    assert "empirical.impulse-response" in output
    assert "mechanism.path-flow" not in output


def test_add_scene_copies_recipe_without_rewriting_project(tmp_path, capsys):
    assert main(["new", "paper", "--destination", str(tmp_path)]) == 0
    project = tmp_path / "paper"
    original_scene = (project / "scenes.py").read_text(encoding="utf-8")
    assert main(["add-scene", str(project), "mechanism.path-flow"]) == 0
    destination = project / "recipes" / "mechanism" / "path_flow"
    assert (destination / "recipe.py").is_file()
    assert (destination / "data" / "path_flow.csv").is_file()
    assert (destination / "data_manifest.toml").is_file()
    copied_manifest = (destination / "data_manifest.toml").read_text(encoding="utf-8")
    assert 'local_path = "recipes/mechanism/path_flow/data/path_flow.csv"' in (
        copied_manifest
    )
    assert not (destination / "project.toml").exists()
    assert (project / "scenes.py").read_text(encoding="utf-8") == original_scene
    assert "Merge" in capsys.readouterr().out


def test_add_scene_refuses_to_overwrite_existing_recipe(tmp_path, capsys):
    assert main(["new", "paper", "--destination", str(tmp_path)]) == 0
    project = tmp_path / "paper"
    assert main(["add-scene", str(project), "empirical.impulse-response"]) == 0
    with pytest.raises(SystemExit) as exit_info:
        main(["add-scene", str(project), "empirical.impulse-response"])
    assert exit_info.value.code == 2
    assert "already exists" in capsys.readouterr().err


def test_checksum_prints_a_manifest_ready_hash(tmp_path, capsys):
    source = tmp_path / "values.csv"
    source.write_text("value\n1\n", encoding="utf-8")
    assert main(["checksum", str(source)]) == 0
    digest, path = capsys.readouterr().out.strip().split("  ", maxsplit=1)
    assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
    assert path == str(source.resolve())


def test_frames_transition_sweep_writes_three_labeled_sheets(
    tmp_path,
    monkeypatch,
    capsys,
):
    calls = []

    def fake_contact_sheet(_video, times, output_dir, **kwargs):
        calls.append((times, kwargs))
        return Path(output_dir) / kwargs.get("sheet_name", "contact_sheet.png")

    monkeypatch.setattr(
        cli,
        "probe_video",
        lambda _video: VideoInfo(
            path="preview.mp4",
            width=854,
            height=480,
            fps=15.0,
            duration=60.0,
            frames=900,
            has_audio=False,
        ),
    )
    monkeypatch.setattr(cli, "extract_contact_sheet", fake_contact_sheet)

    assert (
        main(
            [
                "frames",
                "starter",
                "--video",
                str(tmp_path / "preview.mp4"),
                "--transition-sweep",
            ]
        )
        == 0
    )

    assert [call[1]["sheet_name"] for call in calls] == [
        "settled_states.png",
        "transition_sweep.png",
        "contact_sheet.png",
    ]
    declared = load_project("starter").render.inspection_frames
    settled_count = sum(frame.kind == "settled" for frame in declared)
    transition_count = sum(frame.kind == "transition" for frame in declared)
    assert len(calls[0][0]) == settled_count
    assert len(calls[1][0]) == transition_count * 5
    assert len(calls[2][0]) == settled_count + transition_count * 5
    output = capsys.readouterr().out
    assert "settled states:" in output
    assert "transition sweep:" in output
    assert "combined:" in output


def test_qa_rejects_media_outside_configured_profiles(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "probe_video",
        lambda _video: VideoInfo(
            path="wrong.mp4",
            width=640,
            height=360,
            fps=24.0,
            duration=10.0,
            frames=240,
            has_audio=False,
        ),
    )

    with pytest.raises(SystemExit) as exit_info:
        main(["qa", "starter", "--video", str(tmp_path / "wrong.mp4")])

    assert exit_info.value.code == 2
    assert "configured profile" in capsys.readouterr().err


def test_qa_rejects_audio_in_a_silent_preview(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "probe_video",
        lambda _video: VideoInfo(
            path="preview.mp4",
            width=854,
            height=480,
            fps=15.0,
            duration=60.0,
            frames=900,
            has_audio=True,
        ),
    )

    with pytest.raises(SystemExit) as exit_info:
        main(["qa", "starter", "--video", str(tmp_path / "preview.mp4")])

    assert exit_info.value.code == 2
    assert "unexpectedly contains an audio stream" in capsys.readouterr().err


def test_qa_decodes_opening_and_midpoint_frames(tmp_path, monkeypatch, capsys):
    decoded = []
    monkeypatch.setattr(
        cli,
        "probe_video",
        lambda _video: VideoInfo(
            path="preview.mp4",
            width=854,
            height=480,
            fps=15.0,
            duration=60.0,
            frames=900,
            has_audio=False,
        ),
    )
    monkeypatch.setattr(
        cli,
        "frame_at",
        lambda _video, time: decoded.append(time),
    )

    assert main(["qa", "starter", "--video", str(tmp_path / "preview.mp4")]) == 0
    assert decoded == [0.0, 30.0]
    assert "media decoding" in capsys.readouterr().out


def test_qa_requires_settled_and_transition_inspection_frames(tmp_path, capsys):
    (tmp_path / "scenes.py").write_text("", encoding="utf-8")
    (tmp_path / "project.toml").write_text(
        """
[project]
title = "Incomplete QA"
entrypoint = "scenes.py"
scene = "Scene"
output_file = "incomplete"

[[qa.frame]]
time = 1.0
label = "only settled"
kind = "settled"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exit_info:
        main(["qa", str(tmp_path)])

    assert exit_info.value.code == 2
    assert "missing: transition" in capsys.readouterr().err


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
