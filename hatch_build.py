"""Include copyable project resources in built wheels without preview media."""

from __future__ import annotations

import runpy
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

_MANIFEST = runpy.run_path(
    str(Path(__file__).resolve().with_name("build_resource_manifest.py"))
)
iter_resource_files = _MANIFEST["iter_resource_files"]


class CustomBuildHook(BuildHookInterface):
    """Map authoring resources into ``econ_manim/_resources`` at build time."""

    def initialize(self, version: str, build_data: dict) -> None:
        del version
        root = Path(self.root)
        force_include = build_data.setdefault("force_include", {})
        for relative in iter_resource_files(root):
            destination = "econ_manim/_resources/" + relative.as_posix()
            force_include[str(root / relative)] = destination
