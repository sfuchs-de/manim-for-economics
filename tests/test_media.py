from PIL import Image

from econ_manim import media


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
