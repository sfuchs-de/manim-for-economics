"""Cross-platform command line interface for the paper-video workflow."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import py_compile
import re
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from .config import ConfigError, load_project, validate_data_manifest
from .media import extract_contact_sheet, probe_video
from .templates import PROJECT_TEMPLATES, get_template, template_names, template_source
from .theme import THEMES, theme_names


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


def _render(
    project: Path,
    *,
    preview: bool,
    scene: str | None,
    overlay: bool,
    theme: str | None,
) -> Path:
    config = load_project(project)
    selected_scene = scene or config.scene
    selected_theme = theme or config.theme
    width = config.render.preview_width if preview else config.render.width
    height = config.render.preview_height if preview else config.render.height
    fps = config.render.preview_fps if preview else config.render.fps
    quality = "-ql" if preview else "-qh"
    theme_suffix = f"_{selected_theme}" if theme else ""
    output_name = (
        f"{config.output_file}_{'preview' if preview else '1080p'}{theme_suffix}"
    )
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
        env={
            "ECON_MANIM_QA": "1" if overlay else "0",
            "ECON_MANIM_THEME": selected_theme,
        },
    )
    candidates = sorted(
        (config.root / "build").glob(f"**/{output_name}.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise ConfigError(f"render completed without the expected output {output_name}.mp4")
    return candidates[0]


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
    starter = template_source(args.template, repo_root)
    selected_theme = args.theme or get_template(args.template).default_theme
    destination_root = Path(args.destination).expanduser().resolve()
    target = destination_root / args.name
    if target.exists():
        raise ConfigError(f"destination already exists: {target}")
    shutil.copytree(
        starter,
        target,
        ignore=shutil.ignore_patterns(
            "build",
            "media",
            "preview",
            "__pycache__",
            "*.pyc",
        ),
    )
    project_file = target / "project.toml"
    project_text = project_file.read_text(encoding="utf-8")
    project_text = project_text.replace("My Economics Paper", args.name.replace("-", " ").title())
    project_text = project_text.replace("my_economics_paper", args.name.replace("-", "_"))
    project_text = re.sub(
        r'(?m)^theme = "[^"]+"$',
        f'theme = "{selected_theme}"',
        project_text,
        count=1,
    )
    project_file.write_text(project_text, encoding="utf-8")
    print(
        f"Created {target} from the {args.template!r} template "
        f"with the {selected_theme!r} theme"
    )
    print(f"Next: edit {target / 'paper_brief.md'}")
    return 0


def command_templates(args: argparse.Namespace) -> int:
    del args
    for template in PROJECT_TEMPLATES:
        print(f"{template.name}\n  {template.title}")
        print(f"  Use when: {template.use_when}.")
        print(f"  Sequence: {template.sequence}.")
        print(f"  Informed by: {template.informed_by}.")
        print(f"  Default theme: {template.default_theme}.\n")
    return 0


def command_themes(args: argparse.Namespace) -> int:
    del args
    for name, theme in THEMES.items():
        print(f"{name}\n  {theme.description}.")
        print(
            "  Colors: "
            f"background {theme.background} · ink {theme.foreground} · "
            f"blue {theme.blue} · green {theme.green} · orange {theme.orange}.\n"
        )
    return 0


def command_demo(args: argparse.Namespace) -> int:
    """Render and inspect the bundled starter as an end-to-end installation check."""

    if command_doctor(argparse.Namespace(strict=True)):
        return 1
    repo_root = Path(__file__).resolve().parents[2]
    project = repo_root / "starter"
    if not project.is_dir():
        raise ConfigError(
            "the bundled demo requires a repository checkout containing starter/"
        )
    video = _render(
        project,
        preview=True,
        scene=None,
        overlay=not args.no_overlay,
        theme=args.theme,
    )
    config = load_project(project)
    frames = config.render.inspection_frames
    sheet = extract_contact_sheet(
        video,
        tuple(frame.time for frame in frames),
        config.root / "build" / "qa",
        labels=tuple(frame.label for frame in frames),
        kinds=tuple(frame.kind for frame in frames),
    )
    for message in validate_data_manifest(config.root):
        print(f"[OK] data: {message}")
    print(f"[OK] preview: {video}")
    print(f"[OK] contact sheet: {sheet}")
    print(json.dumps(asdict(probe_video(video)), indent=2))
    return 0


def command_preview(args: argparse.Namespace) -> int:
    video = _render(
        Path(args.project),
        preview=True,
        scene=args.scene,
        overlay=args.overlay,
        theme=args.theme,
    )
    print(json.dumps(asdict(probe_video(video)), indent=2))
    return 0


def command_render(args: argparse.Namespace) -> int:
    video = _render(
        Path(args.project),
        preview=False,
        scene=args.scene,
        overlay=False,
        theme=args.theme,
    )
    print(json.dumps(asdict(probe_video(video)), indent=2))
    return 0


def command_frames(args: argparse.Namespace) -> int:
    config = load_project(args.project)
    video = Path(args.video).resolve() if args.video else _find_video(config)
    if args.times:
        times = tuple(args.times)
        labels = None
        kinds = None
    elif config.render.inspection_frames:
        times = tuple(frame.time for frame in config.render.inspection_frames)
        labels = tuple(frame.label for frame in config.render.inspection_frames)
        kinds = tuple(frame.kind for frame in config.render.inspection_frames)
    else:
        times = config.render.key_times
        labels = None
        kinds = None
    sheet = extract_contact_sheet(
        video,
        times,
        config.root / "build" / "qa",
        labels=labels,
        kinds=kinds,
    )
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
    out_of_range = [
        frame
        for frame in config.render.inspection_frames
        if frame.time > info.duration
    ]
    if out_of_range:
        details = ", ".join(
            f"{frame.label} ({frame.time:.2f}s)" for frame in out_of_range
        )
        raise ConfigError(
            f"inspection frames exceed the {info.duration:.2f}s video duration: {details}"
        )
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

    templates = subparsers.add_parser(
        "templates",
        help="list the available paper-story templates",
    )
    templates.set_defaults(handler=command_templates)

    themes = subparsers.add_parser(
        "themes",
        help="list the available visual theme presets",
    )
    themes.set_defaults(handler=command_themes)

    demo = subparsers.add_parser(
        "demo",
        help="render and inspect the bundled starter end to end",
    )
    demo.add_argument("--theme", choices=theme_names())
    demo.add_argument(
        "--no-overlay",
        action="store_true",
        help="hide safe-area guides in the demo preview",
    )
    demo.set_defaults(handler=command_demo)

    new = subparsers.add_parser("new", help="create a paper project from a template")
    new.add_argument("name")
    new.add_argument("--destination", default="projects")
    new.add_argument(
        "--template",
        choices=template_names(),
        default="general",
        help="narrative grammar to copy (default: general)",
    )
    new.add_argument(
        "--theme",
        choices=theme_names(),
        help="visual preset; defaults to the selected template's example theme",
    )
    new.set_defaults(handler=command_new)

    for name, handler, help_text in (
        ("preview", command_preview, "render a low-resolution draft"),
        ("render", command_render, "render the silent 1080p master"),
    ):
        render_parser = subparsers.add_parser(name, help=help_text)
        render_parser.add_argument("project")
        render_parser.add_argument("--scene")
        render_parser.add_argument("--theme", choices=theme_names())
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
