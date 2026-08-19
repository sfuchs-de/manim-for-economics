import runpy
from pathlib import Path

from econ_manim.resources import resource_directory

ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = runpy.run_path(str(ROOT / "build_resource_manifest.py"))
EXCLUDED_PARTS = _MANIFEST["EXCLUDED_PARTS"]
EXCLUDED_SUFFIXES = _MANIFEST["EXCLUDED_SUFFIXES"]
iter_resource_files = _MANIFEST["iter_resource_files"]


def test_build_hook_includes_copyable_resources_without_generated_media():
    files = iter_resource_files(ROOT)
    assert Path("starter/project.toml") in files
    assert Path("templates/projects/method-theory/project.toml") in files
    assert Path("templates/scenes/method/adjoint_sweep/recipe.py") in files
    assert all(not EXCLUDED_PARTS.intersection(path.parts) for path in files)
    assert all(path.suffix.lower() not in EXCLUDED_SUFFIXES for path in files)


def test_resource_resolver_uses_the_source_checkout_during_development():
    with resource_directory("starter") as starter:
        assert starter == ROOT / "starter"
        assert (starter / "project.toml").is_file()
