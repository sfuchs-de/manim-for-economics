import csv
import re
from pathlib import Path

from econ_manim.config import load_data_manifest, load_project, validate_data_manifest
from econ_manim.media import probe_video

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = (
    ROOT / "starter",
    ROOT / "templates" / "projects" / "mechanism-led",
    ROOT / "templates" / "projects" / "agent-choice-welfare",
    ROOT / "examples" / "format_gallery",
    ROOT / "examples" / "economic_diversity",
    ROOT / "templates" / "scenes" / "mechanism" / "path_flow",
    ROOT / "templates" / "scenes" / "mechanism" / "channel_decomposition",
    ROOT / "templates" / "scenes" / "empirical" / "coefficient_intervals",
    ROOT / "templates" / "scenes" / "empirical" / "impulse_response",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")


def test_every_bundled_project_is_locally_complete():
    for project_root in PROJECTS:
        config = load_project(project_root)
        assert config.entrypoint.is_file()
        assert (project_root / "paper_brief.md").is_file()
        assert (project_root / "storyboard.md").is_file()
        assert (project_root / "data_manifest.toml").is_file()
        assert config.render.inspection_frames
        assert validate_data_manifest(project_root)
        entries = load_data_manifest(project_root)
        assert all(entry.local_path and entry.sha256 for entry in entries)


def test_case_study_sources_are_local_and_checksummed():
    entries = load_data_manifest(ROOT / "examples" / "economic_diversity")
    assert entries
    assert all(entry.local_path and entry.sha256 for entry in entries)


def test_case_study_tables_have_expected_shapes_and_add_up():
    data_dir = ROOT / "examples" / "economic_diversity" / "data"
    with (data_dir / "figure3_point_estimates.csv").open(
        encoding="utf-8",
        newline="",
    ) as handle:
        paths = list(csv.DictReader(handle))
    assert [int(row["horizon"]) for row in paths] == list(range(21))
    assert all(len(row) == 5 for row in paths)

    with (data_dir / "table2_welfare.csv").open(
        encoding="utf-8",
        newline="",
    ) as handle:
        welfare = list(csv.DictReader(handle))
    assert len(welfare) == 4
    for row in welfare:
        direct = float(row["direct_effect"])
        second = float(row["second_order"])
        total = float(row["total"])
        assert round(direct + second, 2) == total


def test_documentation_has_no_broken_relative_links():
    for document in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in document.relative_to(ROOT).parts):
            continue
        text = document.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            if (
                not raw_target
                or raw_target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            target = raw_target.split("#", 1)[0]
            assert (document.parent / target).resolve().exists(), (
                f"{document.relative_to(ROOT)} links to missing {raw_target}"
            )


def test_tracked_sources_do_not_embed_private_machine_paths():
    checked_suffixes = {".cff", ".csv", ".md", ".py", ".toml", ".yaml", ".yml"}
    excluded_parts = {".git", ".venv", "build", "media", "__pycache__"}
    mac_home_prefix = "/" + "Users" + "/"
    windows_home_prefix = "C:" + "\\" + "Users" + "\\"
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        if excluded_parts.intersection(path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        assert mac_home_prefix not in text
        assert windows_home_prefix not in text


def test_repository_contains_no_symlinks():
    excluded_parts = {".git", ".venv", "build", "media", "__pycache__"}
    symlinks = [
        path
        for path in ROOT.rglob("*")
        if path.is_symlink()
        and not excluded_parts.intersection(path.relative_to(ROOT).parts)
    ]
    assert not symlinks


def test_curated_previews_decode_without_external_assets():
    previews = sorted(ROOT.glob("**/preview/*.mp4"))
    assert len(previews) >= 5
    for preview in previews:
        info = probe_video(preview)
        assert info.width == 854
        assert info.height == 480
        assert abs(info.fps - 15) < 0.01
        assert info.duration > 1
        assert not info.has_audio
