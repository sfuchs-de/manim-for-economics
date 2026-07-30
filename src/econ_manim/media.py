"""Video probing and deterministic QA frame extraction using PyAV."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path

import av
from PIL import Image, ImageDraw


@dataclass(frozen=True, slots=True)
class VideoInfo:
    path: str
    width: int
    height: int
    fps: float
    duration: float
    frames: int | None
    has_audio: bool


def probe_video(path: str | Path) -> VideoInfo:
    source = Path(path).resolve()
    with av.open(str(source)) as container:
        stream = container.streams.video[0]
        fps = float(stream.average_rate) if stream.average_rate else 0.0
        if stream.duration is not None:
            duration = float(stream.duration * stream.time_base)
        elif container.duration is not None:
            duration = float(container.duration / av.time_base)
        else:
            duration = 0.0
        return VideoInfo(
            path=str(source),
            width=int(stream.codec_context.width),
            height=int(stream.codec_context.height),
            fps=fps,
            duration=duration,
            frames=int(stream.frames) if stream.frames else None,
            has_audio=bool(container.streams.audio),
        )


def video_info_dict(path: str | Path) -> dict:
    return asdict(probe_video(path))


def frame_at(path: str | Path, time_seconds: float) -> Image.Image:
    if time_seconds < 0:
        raise ValueError("frame time cannot be negative")
    with av.open(str(Path(path).resolve())) as container:
        seek_to = int(max(0.0, time_seconds - 1.0) * av.time_base)
        container.seek(seek_to, backward=True)
        candidate = None
        for frame in container.decode(video=0):
            candidate = frame
            frame_time = float(frame.time or 0.0)
            if frame_time >= time_seconds:
                break
        if candidate is None:
            raise ValueError(f"could not decode a frame at {time_seconds:.2f}s")
        return candidate.to_image().convert("RGB")


def extract_contact_sheet(
    video: str | Path,
    times: tuple[float, ...],
    output_dir: str | Path,
    *,
    columns: int = 3,
    thumbnail_width: int = 480,
) -> Path:
    if not times:
        raise ValueError("at least one inspection time is required")
    target = Path(output_dir).resolve()
    frames_dir = target / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    thumbnails: list[tuple[float, Image.Image]] = []
    for index, time_seconds in enumerate(times):
        image = frame_at(video, time_seconds)
        image_path = frames_dir / f"{index + 1:02d}_{time_seconds:06.2f}s.png"
        image.save(image_path)
        ratio = thumbnail_width / image.width
        thumb = image.resize((thumbnail_width, int(image.height * ratio)))
        thumbnails.append((time_seconds, thumb))

    label_height = 30
    cell_width = thumbnail_width
    cell_height = thumbnails[0][1].height + label_height
    rows = math.ceil(len(thumbnails) / columns)
    sheet = Image.new("RGB", (cell_width * columns, cell_height * rows), "#101922")
    draw = ImageDraw.Draw(sheet)
    for index, (time_seconds, image) in enumerate(thumbnails):
        x = (index % columns) * cell_width
        y = (index // columns) * cell_height
        sheet.paste(image, (x, y))
        draw.text((x + 10, y + image.height + 7), f"{time_seconds:.2f}s", fill="#F1E9DA")
    sheet_path = target / "contact_sheet.png"
    sheet.save(sheet_path)
    return sheet_path
