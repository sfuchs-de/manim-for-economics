"""Exercise copyable resources from an unpacked wheel, outside the checkout."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(command: list[str], *, cwd: Path, pythonpath: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(pythonpath)
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: wheel_smoke.py path/to/package.whl")
    wheel = Path(sys.argv[1]).resolve()
    if not wheel.is_file():
        raise SystemExit(f"wheel does not exist: {wheel}")
    with tempfile.TemporaryDirectory(prefix="econ-manim-wheel-smoke-") as temporary:
        root = Path(temporary)
        unpacked = root / "wheel"
        unpacked.mkdir()
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(unpacked)
        resources = unpacked / "econ_manim" / "_resources"
        required = (
            resources / "starter" / "project.toml",
            resources / "templates" / "projects" / "method-theory" / "project.toml",
            resources
            / "templates"
            / "scenes"
            / "empirical"
            / "spatial_policy_ladder"
            / "recipe.py",
        )
        if not all(path.is_file() for path in required):
            raise SystemExit("wheel is missing copyable project resources")
        if any(resources.rglob("*.mp4")) or any(resources.rglob("preview")):
            raise SystemExit("wheel contains curated previews or generated media")

        workspace = root / "workspace"
        workspace.mkdir()
        base = [sys.executable, "-m", "econ_manim.cli"]
        run(
            [*base, "new", "paper", "--destination", ".", "--template", "method-theory"],
            cwd=workspace,
            pythonpath=unpacked,
        )
        run(
            [*base, "add-scene", "paper", "empirical.spatial-policy-ladder"],
            cwd=workspace,
            pythonpath=unpacked,
        )
        copied = (
            workspace
            / "paper"
            / "recipes"
            / "empirical"
            / "spatial_policy_ladder"
            / "recipe.py"
        )
        if not copied.is_file():
            raise SystemExit("installed add-scene did not copy the selected recipe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
