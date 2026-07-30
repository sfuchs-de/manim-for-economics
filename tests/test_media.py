from PIL import Image

from econ_manim import media
from econ_manim.config import InspectionFrame


def test_named_contact_sheet_replaces_stale_frames(tmp_path, monkeypatch):
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    stale = frames_dir / "stale.png"
    stale.write_bytes(b"old")
    monkeypatch.setattr(
        media,
        "frame_at",
        lambda _video, _time: Image.new("RGB", (160, 90), "#101922"),
    )

    sheet = media.extract_contact_sheet(
        "unused.mp4",
        (1.0, 2.0),
        tmp_path,
        labels=("opening", "handoff"),
        kinds=("settled", "transition"),
        thumbnail_width=160,
    )

    assert sheet.is_file()
    assert not stale.exists()
    assert sorted(path.name for path in frames_dir.glob("*.png")) == [
        "01_001.00s.png",
        "02_002.00s.png",
    ]


def test_contact_sheet_supports_named_outputs_and_frame_directories(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        media,
        "frame_at",
        lambda _video, _time: Image.new("RGB", (160, 90), "#101922"),
    )

    sheet = media.extract_contact_sheet(
        "unused.mp4",
        (1.0,),
        tmp_path,
        sheet_name="settled_states.png",
        frames_subdir="frames/settled",
        thumbnail_width=160,
    )

    assert sheet == tmp_path / "settled_states.png"
    assert (tmp_path / "frames" / "settled" / "01_001.00s.png").is_file()


def test_transition_sweep_samples_and_clamps_each_declared_transition():
    frames = (
        InspectionFrame(time=0.2, label="opening handoff", kind="transition"),
        InspectionFrame(time=5.0, label="stable view", kind="settled"),
        InspectionFrame(time=9.8, label="closing handoff", kind="transition"),
    )

    sweep = media.transition_sweep_frames(frames, duration=10.0)

    assert len(sweep) == 10
    assert tuple(frame.time for frame in sweep[:5]) == (0.0, 0.0, 0.2, 0.45, 0.7)
    assert tuple(frame.time for frame in sweep[-5:]) == (9.3, 9.55, 9.8, 10.0, 10.0)
    assert all(frame.kind == "transition" for frame in sweep)
    assert sweep[0].label == "opening handoff (-0.50s)"
