"""Video probing and deterministic QA frame extraction using PyAV."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path

import av
from PIL import Image, ImageDraw

from .config import InspectionFrame

TRANSITION_SWEEP_OFFSETS = (-0.50, -0.25, 0.0, 0.25, 0.50)
MAX_INTERVAL_SWEEP_FRAMES = 72


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


def probe_audio_duration(path: str | Path) -> float:
    """Return an audio file's duration in seconds using PyAV."""

    source = Path(path).resolve()
    with av.open(str(source)) as container:
        streams = tuple(container.streams.audio)
        if not streams:
            raise ValueError(f"audio file has no audio stream: {source}")
        stream = streams[0]
        if stream.duration is not None:
            duration = float(stream.duration * stream.time_base)
        elif container.duration is not None:
            duration = float(container.duration / av.time_base)
        else:
            raise ValueError(f"audio duration is unavailable: {source}")
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"audio duration must be positive: {source}")
    return duration


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


def transition_sweep_frames(
    frames: tuple[InspectionFrame, ...],
    duration: float,
    *,
    offsets: tuple[float, ...] = TRANSITION_SWEEP_OFFSETS,
) -> tuple[InspectionFrame, ...]:
    """Expand declared transitions into clamped before/during/after samples."""

    if duration <= 0:
        raise ValueError("video duration must be positive")
    sweep: list[InspectionFrame] = []
    for frame in frames:
        if frame.kind != "transition":
            continue
        for offset in offsets:
            time = min(duration, max(0.0, frame.time + offset))
            sweep.append(
                InspectionFrame(
                    time=time,
                    label=f"{frame.label} ({offset:+.2f}s)",
                    kind="transition",
                )
            )
    return tuple(sweep)


def interval_sweep_frames(
    duration: float,
    interval: float,
    *,
    include_final: bool = True,
    max_frames: int = MAX_INTERVAL_SWEEP_FRAMES,
) -> tuple[InspectionFrame, ...]:
    """Sample a video regularly and include its final settled frame.

    Regular sampling complements declared transition frames: it catches scenes
    that are dense, blank, or visually unstable between the named checkpoints.
    The final sample sits just inside the media duration so compressed videos do
    not require a frame exactly at end-of-stream.
    """

    if duration <= 0:
        raise ValueError("video duration must be positive")
    if interval <= 0:
        raise ValueError("frame interval must be positive")
    if max_frames <= 0:
        raise ValueError("max_frames must be positive")

    times = [index * interval for index in range(math.ceil(duration / interval))]
    times = [time for time in times if time < duration]
    final_time = max(0.0, duration - 0.10)
    if include_final and (not times or final_time - times[-1] > 0.25):
        times.append(final_time)
    if len(times) > max_frames:
        minimum = duration / max_frames
        raise ValueError(
            f"interval sweep would create {len(times)} frames; "
            f"use an interval of at least {minimum:.2f} seconds"
        )

    frames = []
    for index, time in enumerate(times):
        is_final = include_final and index == len(times) - 1 and time == final_time
        frames.append(
            InspectionFrame(
                time=time,
                label="final frame" if is_final else f"regular sample {index + 1}",
                kind="interval",
            )
        )
    return tuple(frames)


def extract_contact_sheet(
    video: str | Path,
    times: tuple[float, ...],
    output_dir: str | Path,
    *,
    labels: tuple[str, ...] | None = None,
    kinds: tuple[str, ...] | None = None,
    columns: int = 3,
    thumbnail_width: int = 480,
    sheet_name: str = "contact_sheet.png",
    frames_subdir: str = "frames",
) -> Path:
    if not times:
        raise ValueError("at least one inspection time is required")
    if labels is not None and len(labels) != len(times):
        raise ValueError("labels must match the number of inspection times")
    if kinds is not None and len(kinds) != len(times):
        raise ValueError("kinds must match the number of inspection times")
    target = Path(output_dir).resolve()
    frames_dir = target / frames_subdir
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in frames_dir.glob("*.png"):
        old_frame.unlink()
    thumbnails: list[tuple[float, str, str, Image.Image]] = []
    for index, time_seconds in enumerate(times):
        image = frame_at(video, time_seconds)
        label = labels[index] if labels else ""
        kind = kinds[index] if kinds else ""
        image_path = frames_dir / f"{index + 1:02d}_{time_seconds:06.2f}s.png"
        image.save(image_path)
        ratio = thumbnail_width / image.width
        thumb = image.resize((thumbnail_width, int(image.height * ratio)))
        thumbnails.append((time_seconds, label, kind, thumb))

    label_height = 54 if labels or kinds else 30
    cell_width = thumbnail_width
    cell_height = thumbnails[0][3].height + label_height
    rows = math.ceil(len(thumbnails) / columns)
    sheet = Image.new("RGB", (cell_width * columns, cell_height * rows), "#101922")
    draw = ImageDraw.Draw(sheet)
    for index, (time_seconds, label, kind, image) in enumerate(thumbnails):
        x = (index % columns) * cell_width
        y = (index // columns) * cell_height
        sheet.paste(image, (x, y))
        metadata = f"{kind.upper()} · {time_seconds:.2f}s" if kind else f"{time_seconds:.2f}s"
        draw.text((x + 10, y + image.height + 6), metadata, fill="#F1E9DA")
        if label:
            draw.text((x + 10, y + image.height + 27), label, fill="#9DAAB7")
    sheet_path = target / sheet_name
    sheet.save(sheet_path)
    return sheet_path
