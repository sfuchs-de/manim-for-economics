import json
import shutil
from pathlib import Path

import pytest

import econ_manim.narration as narration
from econ_manim.cli import build_parser, main
from econ_manim.config import ConfigError
from econ_manim.narration import load_narration_script, write_narration_recorder


def narration_project(tmp_path: Path) -> Path:
    source = Path(__file__).resolve().parents[1] / "starter"
    project = tmp_path / "paper"
    shutil.copytree(source, project)
    (project / "narration.toml").write_text(
        """
[narration]
rate = 120
target_loudness_lufs = -18

[[cue]]
id = "opening"
text = "A transport improvement lowers costs."

[[cue]]
id = "result"
text = "The welfare effect also depends on equilibrium adjustment."
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return project


def test_recorder_is_a_self_contained_script_specific_html(tmp_path):
    project = narration_project(tmp_path)
    output = write_narration_recorder(project)
    page = output.read_text(encoding="utf-8")

    assert output == project / "build" / "narration-recorder.html"
    assert "A transport improvement lowers costs." in page
    assert "Recorded locally. Nothing is uploaded." in page
    assert "https://" not in page
    assert "showDirectoryPicker" in page
    assert "__SCRIPT_JSON__" not in page


def test_recorder_uses_matching_manifest_durations(tmp_path):
    project = narration_project(tmp_path)
    manifest_dir = project / "assets" / "narration"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "cues": {
                    "opening": {
                        "duration": 7.25,
                        "text": "A transport improvement lowers costs.",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    script = load_narration_script(project)

    assert script.cues[0].target_duration == 7.25
    assert script.cues[1].target_duration == 4.0


def test_recorder_ignores_stale_manifest_duration(tmp_path):
    project = narration_project(tmp_path)
    manifest_dir = project / "assets" / "narration"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {"cues": {"opening": {"duration": 99, "text": "An older script."}}}
        ),
        encoding="utf-8",
    )

    script = load_narration_script(project)

    assert script.cues[0].target_duration == 2.5


def test_recorder_rejects_duplicate_cue_ids(tmp_path):
    project = narration_project(tmp_path)
    with (project / "narration.toml").open("a", encoding="utf-8") as handle:
        handle.write('\n[[cue]]\nid = "opening"\ntext = "Duplicate."\n')

    with pytest.raises(ConfigError, match="duplicate narration cue id"):
        load_narration_script(project)


def test_recorder_embeds_script_aligned_reference_frames(tmp_path, monkeypatch):
    project = narration_project(tmp_path)
    video = tmp_path / "render.mp4"
    subtitles = tmp_path / "render.srt"
    video.write_bytes(b"video")
    subtitles.write_text(
        """1
00:00:00,000 --> 00:00:03,000
A transport improvement lowers costs.

2
00:00:03,350 --> 00:00:08,000
The welfare effect also depends on equilibrium adjustment.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    def fake_run(command, check):
        assert check
        Path(command[-1]).write_bytes(b"jpeg")

    monkeypatch.setattr(narration.subprocess, "run", fake_run)

    output = narration.write_narration_recorder(
        project,
        video=video,
        subtitles=subtitles,
    )
    page = output.read_text(encoding="utf-8")

    assert page.count("data:image/jpeg;base64,anBlZw==") == 2
    assert '"visual_time": 2.8' in page


def test_recorder_rejects_stills_from_a_different_script(tmp_path, monkeypatch):
    project = narration_project(tmp_path)
    video = tmp_path / "render.mp4"
    subtitles = tmp_path / "render.srt"
    video.write_bytes(b"video")
    subtitles.write_text(
        """1
00:00:00,000 --> 00:00:03,000
Old opening text.

2
00:00:03,350 --> 00:00:08,000
The welfare effect also depends on equilibrium adjustment.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    with pytest.raises(ConfigError, match="subtitle text does not match"):
        narration.write_narration_recorder(
            project,
            video=video,
            subtitles=subtitles,
        )


def test_subtitle_alignment_accepts_spoken_decimal_formatting():
    assert narration._alignment_text("about point zero four basis points") == (
        narration._alignment_text("about 0.04 basis points")
    )


def test_record_narration_cli_accepts_an_explicit_output(tmp_path):
    project = narration_project(tmp_path)
    output = tmp_path / "coauthor-recorder.html"

    assert main(["record-narration", str(project), "--output", str(output)]) == 0
    assert output.is_file()


def test_record_narration_cli_can_omit_reference_stills():
    parsed = build_parser().parse_args(
        ["record-narration", "project", "--no-stills"]
    )
    assert parsed.no_stills is True


def test_narration_check_reports_cue_reading_rates(tmp_path, capsys):
    project = narration_project(tmp_path)

    assert main(["narration-check", str(project)]) == 0
    output = capsys.readouterr().out
    assert "[OK] opening" in output
    assert "120.0 wpm" in output
    assert "timing estimate" in output


def test_narration_check_rejects_reading_rates_above_the_gate(tmp_path):
    project = narration_project(tmp_path)

    with pytest.raises(SystemExit) as exit_info:
        main(["narration-check", str(project), "--max-wpm", "100"])
    assert exit_info.value.code == 2


def test_prepare_narration_fails_before_writing_when_a_cue_is_missing(
    tmp_path, monkeypatch
):
    project = narration_project(tmp_path)
    recordings = tmp_path / "recordings"
    recordings.mkdir()
    (recordings / "opening.webm").write_bytes(b"placeholder")
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    with pytest.raises(ConfigError, match="recording is missing for cue 'result'"):
        from econ_manim.narration import prepare_recorded_narration

        prepare_recorded_narration(project, recordings)

    assert not (project / "assets" / "narration" / "manifest.json").exists()


def test_prepare_narration_writes_scene_compatible_manifest(tmp_path, monkeypatch):
    project = narration_project(tmp_path)
    recordings = tmp_path / "recordings"
    recordings.mkdir()
    (recordings / "opening.webm").write_bytes(b"opening")
    (recordings / "result.ogg").write_bytes(b"result")

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    def fake_run(command, check):
        assert check
        Path(command[-1]).write_bytes(b"prepared-wave")

    monkeypatch.setattr(narration.subprocess, "run", fake_run)
    monkeypatch.setattr(narration, "probe_audio_duration", lambda path: 3.25)

    manifest_path = narration.prepare_recorded_narration(
        project,
        recordings,
        speaker="Coauthor",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["provider"] == "human-recording"
    assert manifest["speaker"] == "Coauthor"
    assert manifest["sample_rate_hz"] == 48000
    assert set(manifest["cues"]) == {"opening", "result"}
    assert manifest["cues"]["opening"]["file"] == "assets/narration/opening.wav"
    assert manifest["cues"]["opening"]["duration"] == 3.25


def test_prepare_narration_rejects_recordings_from_an_old_script(tmp_path, monkeypatch):
    project = narration_project(tmp_path)
    recordings = tmp_path / "recordings"
    recordings.mkdir()
    (recordings / "recording-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "narration_sha256": "0" * 64,
                "cues": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    with pytest.raises(ConfigError, match="different narration script"):
        narration.prepare_recorded_narration(project, recordings)
