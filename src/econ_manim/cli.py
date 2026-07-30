"""Cross-platform command line interface for the paper-video workflow."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import py_compile
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from .config import ConfigError, load_project, validate_data_manifest
from .media import extract_contact_sheet, probe_video


def _run(command: list[str], *, cwd: Path, env: dict | None = None) -> None:
    import os

    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    print("$", " ".join(command))
    subprocess.run(command, cwd=cwd, env=process_env, check=True)


def _find_video(config, *, prefer_master: bool = False) -> Path:
    candidates = sorted(
        (config.root / "build").glob(f"**/{config.output_file}*.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if prefer_master:
        masters = [path for path in candidates if "1080p" in str(path) or "final" in str(path)]
        if masters:
            return masters[0]
    if not candidates:
        raise ConfigError(
            f"no rendered video found below {config.root / 'build'}; run preview or render first"
        )
    return candidates[0]


def _render(project: Path, *, preview: bool, scene: str | None, overlay: bool) -> Path:
    config = load_project(project)
    selected_scene = scene or config.scene
    width = config.render.preview_width if preview else config.render.width
    height = config.render.preview_height if preview else config.render.height
    fps = config.render.preview_fps if preview else config.render.fps
    quality = "-ql" if preview else "-qh"
    output_name = f"{config.output_file}_{'preview' if preview else '1080p'}"
    media_dir = config.root / "build" / "media"
    command = [
        sys.executable,
        "-m",
        "manim",
        quality,
        "--fps",
        str(fps),
        "-r",
        f"{width},{height}",
        "--media_dir",
        str(media_dir),
        "--output_file",
        output_name,
        str(config.entrypoint),
        selected_scene,
    ]
    _run(
        command,
        cwd=config.root,
        env={"ECON_MANIM_QA": "1" if overlay else "0"},
    )
    return _find_video(config, prefer_master=not preview)


def command_doctor(args: argparse.Namespace) -> int:
    checks = []
    checks.append(("Python >= 3.11", sys.version_info >= (3, 11), sys.version.split()[0]))
    try:
        manim_version = importlib.metadata.version("manim")
        checks.append(("Manim", manim_version == "0.20.1", manim_version))
    except importlib.metadata.PackageNotFoundError:
        checks.append(("Manim", False, "not installed"))
    for binary, required in (("latex", args.strict), ("dvisvgm", args.strict), ("ffmpeg", False)):
        path = shutil.which(binary)
        checks.append((binary, bool(path) or not required, path or "not found (optional)"))
    if sys.platform == "darwin":
        checks.append(("font discovery", bool(shutil.which("system_profiler")), "macOS"))
    elif sys.platform == "win32":
        checks.append(("font discovery", True, "Windows Fonts"))
    else:
        checks.append(("font discovery", bool(shutil.which("fc-match")), "fontconfig"))

    failed = False
    for name, passed, detail in checks:
        marker = "OK" if passed else "FAIL"
        print(f"[{marker:4}] {name}: {detail}")
        failed = failed or not passed
    if not shutil.which("ffmpeg"):
        print("[INFO] FFmpeg is only required for the optional audio command.")
    return int(failed)


def command_new(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    starter = repo_root / "starter"
    destination_root = Path(args.destination).expanduser().resolve()
    target = destination_root / args.name
    if target.exists():
        raise ConfigError(f"destination already exists: {target}")
    shutil.copytree(
        starter,
        target,
        ignore=shutil.ignore_patterns("build", "media", "__pycache__", "*.pyc"),
    )
    project_file = target / "project.toml"
    project_text = project_file.read_text(encoding="utf-8")
    project_text = project_text.replace("My Economics Paper", args.name.replace("-", " ").title())
    project_text = project_text.replace("my_economics_paper", args.name.replace("-", "_"))
    project_file.write_text(project_text, encoding="utf-8")
    print(f"Created {target}")
    print(f"Next: edit {target / 'paper_brief.md'}")
    return 0


def command_preview(args: argparse.Namespace) -> int:
    video = _render(Path(args.project), preview=True, scene=args.scene, overlay=args.overlay)
    print(json.dumps(asdict(probe_video(video)), indent=2))
    return 0


def command_render(args: argparse.Namespace) -> int:
    video = _render(Path(args.project), preview=False, scene=args.scene, overlay=False)
    print(json.dumps(asdict(probe_video(video)), indent=2))
    return 0


def command_frames(args: argparse.Namespace) -> int:
    config = load_project(args.project)
    video = Path(args.video).resolve() if args.video else _find_video(config)
    times = tuple(args.times) if args.times else config.render.key_times
    sheet = extract_contact_sheet(video, times, config.root / "build" / "qa")
    print(sheet)
    return 0


def command_qa(args: argparse.Namespace) -> int:
    config = load_project(args.project)
    print(f"[OK] project: {config.title}")
    py_compile.compile(str(config.entrypoint), doraise=True)
    print(f"[OK] source compiles: {config.entrypoint.name}")
    for message in validate_data_manifest(config.root):
        print(f"[OK] data: {message}")
    try:
        video = Path(args.video).resolve() if args.video else _find_video(config)
    except ConfigError:
        print("[INFO] no render found; media checks skipped")
        return 0
    info = probe_video(video)
    if info.width <= 0 or info.height <= 0 or info.duration <= 0:
        raise ConfigError(f"invalid rendered media: {info}")
    print(json.dumps(asdict(info), indent=2))
    return 0


def command_audio(args: argparse.Namespace) -> int:
    config = load_project(args.project)
    if not config.audio.enabled:
        raise ConfigError("audio.enabled is false in project.toml")
    if not config.audio.track or not config.audio.license or not config.audio.attribution:
        raise ConfigError("audio requires track, license, and attribution")
    if not shutil.which("ffmpeg"):
        raise ConfigError("FFmpeg is required for audio mixing")
    track = (config.root / config.audio.track).resolve()
    if not track.is_file():
        raise ConfigError(f"audio track does not exist: {track}")
    video = _find_video(config, prefer_master=True)
    info = probe_video(video)
    output_dir = config.root / "build" / "final"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{config.output_file}_audio.mp4"
    fade_start = max(0.0, info.duration - 3.0)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-stream_loop",
        "-1",
        "-i",
        str(track),
        "-filter_complex",
        f"[1:a]atrim=0:{info.duration:.3f},afade=t=out:st={fade_start:.3f}:d=3[a]",
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(output),
    ]
    _run(command, cwd=config.root)
    print(json.dumps(asdict(probe_video(output)), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="econ-manim",
        description="Build and verify Manim explainers for economics papers.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="check the local rendering environment")
    doctor.add_argument("--strict", action="store_true", help="require LaTeX and dvisvgm")
    doctor.set_defaults(handler=command_doctor)

    new = subparsers.add_parser("new", help="copy the starter into a new paper project")
    new.add_argument("name")
    new.add_argument("--destination", default="projects")
    new.set_defaults(handler=command_new)

    for name, handler, help_text in (
        ("preview", command_preview, "render a low-resolution draft"),
        ("render", command_render, "render the silent 1080p master"),
    ):
        render_parser = subparsers.add_parser(name, help=help_text)
        render_parser.add_argument("project")
        render_parser.add_argument("--scene")
        if name == "preview":
            render_parser.add_argument("--overlay", action="store_true")
        render_parser.set_defaults(handler=handler)

    frames = subparsers.add_parser("frames", help="extract QA frames and a contact sheet")
    frames.add_argument("project")
    frames.add_argument("--video")
    frames.add_argument("--times", type=float, nargs="+")
    frames.set_defaults(handler=command_frames)

    qa = subparsers.add_parser("qa", help="validate source, provenance, and rendered media")
    qa.add_argument("project")
    qa.add_argument("--video")
    qa.set_defaults(handler=command_qa)

    audio = subparsers.add_parser("audio", help="mix documented music into a rendered master")
    audio.add_argument("project")
    audio.set_defaults(handler=command_audio)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (ConfigError, subprocess.CalledProcessError, OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
