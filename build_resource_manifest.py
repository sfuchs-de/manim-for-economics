"""Select project resources that belong in a built distribution."""

from __future__ import annotations

from pathlib import Path

RESOURCE_ROOTS = (Path("starter"), Path("templates"))
EXCLUDED_PARTS = {"build", "media", "preview", "__pycache__"}
EXCLUDED_SUFFIXES = {".mp3", ".m4a", ".mp4", ".pyc", ".wav"}


def iter_resource_files(root: Path) -> tuple[Path, ...]:
    """Return deterministic, distributable files below ``root``."""

    files = []
    for source_root in RESOURCE_ROOTS:
        for path in (root / source_root).rglob("*"):
            relative = path.relative_to(root)
            if not path.is_file():
                continue
            if EXCLUDED_PARTS.intersection(relative.parts):
                continue
            if path.suffix.lower() in EXCLUDED_SUFFIXES:
                continue
            files.append(relative)
    return tuple(sorted(files))
