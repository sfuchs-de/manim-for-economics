import ast
import csv
import re
from pathlib import Path

from econ_manim.config import load_data_manifest, load_project, validate_data_manifest
from econ_manim.examples import EXAMPLE_PROJECTS
from econ_manim.media import probe_video
from econ_manim.scene_templates import SCENE_TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOTS = (
    ROOT / "starter",
    ROOT / "templates" / "projects",
    ROOT / "templates" / "scenes",
    ROOT / "examples",
)


def bundled_projects() -> tuple[Path, ...]:
    projects = set()
    for source in PROJECT_ROOTS:
        if (source / "project.toml").is_file():
            projects.add(source)
        projects.update(path.parent for path in source.rglob("project.toml"))
    return tuple(sorted(projects))


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")


def test_every_bundled_project_is_locally_complete():
    for project_root in bundled_projects():
        config = load_project(project_root)
        assert config.entrypoint.is_file()
        assert (project_root / "paper_brief.md").is_file()
        assert (project_root / "storyboard.md").is_file()
        assert (project_root / "data_manifest.toml").is_file()
        assert config.render.inspection_frames
        assert validate_data_manifest(project_root)
        entries = load_data_manifest(project_root)
        assert all(entry.local_path and entry.sha256 for entry in entries)


def test_scene_registry_covers_every_atomic_recipe():
    identifiers = [template.identifier for template in SCENE_TEMPLATES]
    assert len(identifiers) == len(set(identifiers))
    registered = {template.source for template in SCENE_TEMPLATES}
    assert len(registered) == len(SCENE_TEMPLATES)
    discovered = {
        path.parent.relative_to(ROOT).as_posix()
        for path in (ROOT / "templates" / "scenes").rglob("project.toml")
    }
    assert registered == discovered


def test_example_registry_covers_every_complete_example():
    identifiers = [example.identifier for example in EXAMPLE_PROJECTS]
    assert len(identifiers) == len(set(identifiers))
    registered = {example.source for example in EXAMPLE_PROJECTS}
    assert len(registered) == len(EXAMPLE_PROJECTS)
    discovered = {
        path.parent.relative_to(ROOT).as_posix()
        for path in (ROOT / "examples").glob("*/project.toml")
    }
    assert registered == discovered


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


def test_bundled_scenes_do_not_import_raw_manim_text():
    """Keep first-party prose on the package's deterministic typography path."""

    source_roots = (ROOT / "src", ROOT / "starter", ROOT / "templates", ROOT / "examples")
    offenders = []
    for source_root in source_roots:
        for path in source_root.rglob("*.py"):
            if path == ROOT / "src" / "econ_manim" / "typography.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or node.module != "manim":
                    continue
                if any(alias.name == "Text" for alias in node.names):
                    offenders.append(path.relative_to(ROOT))
    assert not offenders, f"use econ_manim.ProseText instead of manim.Text: {offenders}"


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
