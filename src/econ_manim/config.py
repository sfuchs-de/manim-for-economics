"""Project and provenance manifest parsing."""

from __future__ import annotations

import hashlib
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .theme import theme_names


class ConfigError(ValueError):
    """Raised for invalid project or data configuration."""


@dataclass(frozen=True, slots=True)
class InspectionFrame:
    time: float
    label: str
    kind: str


@dataclass(frozen=True, slots=True)
class RenderConfig:
    preview_width: int = 854
    preview_height: int = 480
    preview_fps: int = 15
    width: int = 1920
    height: int = 1080
    fps: int = 30
    key_times: tuple[float, ...] = ()
    inspection_frames: tuple[InspectionFrame, ...] = ()


@dataclass(frozen=True, slots=True)
class AudioConfig:
    enabled: bool = False
    track: str = ""
    license: str = ""
    attribution: str = ""
    embedded_narration: bool = False
    music_gain_db: float = -21.0
    narration_gain_db: float = 0.0


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    root: Path
    title: str
    entrypoint: Path
    scene: str
    output_file: str
    theme: str
    render: RenderConfig
    audio: AudioConfig


@dataclass(frozen=True, slots=True)
class DatasetEntry:
    identifier: str
    status: str
    classification: str
    source_url: str
    license: str
    local_path: str
    sha256: str
    transformation: str
    displayed_values: tuple[str, ...]
    note: str


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as error:
        raise ConfigError(f"missing configuration: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML in {path}: {error}") from error


def load_project(project: str | Path) -> ProjectConfig:
    root = Path(project).expanduser().resolve()
    path = root / "project.toml"
    raw = _read_toml(path)
    section = raw.get("project", {})
    render = raw.get("render", {})
    audio = raw.get("audio", {})
    qa = raw.get("qa", {})
    required = ("title", "entrypoint", "scene", "output_file")
    missing = [key for key in required if not section.get(key)]
    if missing:
        raise ConfigError(f"{path} is missing project fields: {', '.join(missing)}")
    entrypoint = root / str(section["entrypoint"])
    if not entrypoint.is_file():
        raise ConfigError(f"entrypoint does not exist: {entrypoint}")
    theme = str(section.get("theme", "midnight")).strip().lower()
    if theme not in theme_names():
        choices = ", ".join(theme_names())
        raise ConfigError(f"{path} has unknown theme {theme!r}; choose one of: {choices}")
    key_times = tuple(float(value) for value in render.get("key_times", ()))
    if any(value < 0 for value in key_times):
        raise ConfigError("render.key_times cannot contain negative values")
    inspection_frames = []
    for index, item in enumerate(qa.get("frame", ())):
        try:
            time = float(item["time"])
        except (KeyError, TypeError, ValueError) as error:
            raise ConfigError(f"qa.frame {index + 1} requires a numeric time") from error
        label = str(item.get("label", "")).strip()
        kind = str(item.get("kind", "")).strip()
        if time < 0:
            raise ConfigError("qa.frame times cannot be negative")
        if not label:
            raise ConfigError(f"qa.frame {index + 1} requires a label")
        if kind not in {"settled", "transition"}:
            raise ConfigError(
                f"qa.frame {index + 1} has invalid kind {kind!r}; "
                "use settled or transition"
            )
        inspection_frames.append(InspectionFrame(time=time, label=label, kind=kind))
    render_config = RenderConfig(
        preview_width=int(render.get("preview_width", 854)),
        preview_height=int(render.get("preview_height", 480)),
        preview_fps=int(render.get("preview_fps", 15)),
        width=int(render.get("width", 1920)),
        height=int(render.get("height", 1080)),
        fps=int(render.get("fps", 30)),
        key_times=key_times,
        inspection_frames=tuple(inspection_frames),
    )
    positive_render_fields = {
        "preview_width": render_config.preview_width,
        "preview_height": render_config.preview_height,
        "preview_fps": render_config.preview_fps,
        "width": render_config.width,
        "height": render_config.height,
        "fps": render_config.fps,
    }
    invalid = [name for name, value in positive_render_fields.items() if value <= 0]
    if invalid:
        raise ConfigError(
            f"{path} has non-positive render fields: {', '.join(invalid)}"
        )
    music_gain_db = float(audio.get("music_gain_db", -21.0))
    narration_gain_db = float(audio.get("narration_gain_db", 0.0))
    if not math.isfinite(music_gain_db) or not math.isfinite(narration_gain_db):
        raise ConfigError("audio gains must be finite decibel values")
    return ProjectConfig(
        root=root,
        title=str(section["title"]),
        entrypoint=entrypoint,
        scene=str(section["scene"]),
        output_file=str(section["output_file"]),
        theme=theme,
        render=render_config,
        audio=AudioConfig(
            enabled=bool(audio.get("enabled", False)),
            track=str(audio.get("track", "")),
            license=str(audio.get("license", "")),
            attribution=str(audio.get("attribution", "")),
            embedded_narration=bool(audio.get("embedded_narration", False)),
            music_gain_db=music_gain_db,
            narration_gain_db=narration_gain_db,
        ),
    )


def load_data_manifest(project: str | Path) -> tuple[DatasetEntry, ...]:
    root = Path(project).expanduser().resolve()
    path = root / "data_manifest.toml"
    raw = _read_toml(path)
    datasets = raw.get("dataset", ())
    if not datasets:
        raise ConfigError(f"{path} requires at least one [[dataset]] entry")
    entries = []
    for index, item in enumerate(datasets):
        identifier = str(item.get("id", "")).strip()
        status = str(item.get("status", "")).strip()
        if not identifier:
            raise ConfigError(f"dataset {index + 1} has no id")
        if status not in {"released", "digitized", "illustrative"}:
            raise ConfigError(
                f"dataset {identifier} has invalid status {status!r}; "
                "use released, digitized, or illustrative"
            )
        classification = str(item.get("classification", "")).strip()
        if classification not in {"actual", "illustrative"}:
            raise ConfigError(
                f"dataset {identifier} has invalid classification "
                f"{classification!r}; use actual or illustrative"
            )
        expected_classification = "illustrative" if status == "illustrative" else "actual"
        if classification != expected_classification:
            raise ConfigError(
                f"dataset {identifier}: status {status!r} requires "
                f"classification {expected_classification!r}"
            )
        source_url = str(item.get("source_url", "")).strip()
        license_name = str(item.get("license", "")).strip()
        if status != "illustrative" and (not source_url or not license_name):
            raise ConfigError(f"dataset {identifier} requires source_url and license")
        transformation = str(item.get("transformation", "")).strip()
        if not transformation:
            raise ConfigError(f"dataset {identifier} requires transformation")
        displayed_values = tuple(
            str(value).strip() for value in item.get("displayed_values", ())
        )
        if not displayed_values or any(not value for value in displayed_values):
            raise ConfigError(f"dataset {identifier} requires displayed_values")
        local_path = str(item.get("local_path", "")).strip()
        checksum = str(item.get("sha256", "")).strip().lower()
        if local_path and not checksum:
            raise ConfigError(f"dataset {identifier} requires sha256 for its local file")
        entries.append(
            DatasetEntry(
                identifier=identifier,
                status=status,
                classification=classification,
                source_url=source_url,
                license=license_name,
                local_path=local_path,
                sha256=checksum,
                transformation=transformation,
                displayed_values=displayed_values,
                note=str(item.get("note", "")).strip(),
            )
        )
    return tuple(entries)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_data_manifest(project: str | Path) -> list[str]:
    root = Path(project).expanduser().resolve()
    messages: list[str] = []
    for entry in load_data_manifest(root):
        if not entry.local_path:
            messages.append(f"{entry.identifier}: metadata-only ({entry.status})")
            continue
        local = root / entry.local_path
        if not local.is_file():
            raise ConfigError(f"{entry.identifier}: missing local file {local}")
        actual = sha256_file(local)
        if entry.sha256 and actual != entry.sha256:
            raise ConfigError(
                f"{entry.identifier}: checksum mismatch; expected {entry.sha256}, got {actual}"
            )
        messages.append(
            f"{entry.identifier}: {entry.status}/{entry.classification}, sha256={actual}"
        )
    return messages
