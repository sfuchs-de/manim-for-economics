"""Resolve bundled project resources in source checkouts and installed wheels."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory

from .config import ConfigError


def _copy_traversable(source, destination: Path) -> None:
    """Materialize a package-resource tree without assuming a filesystem loader."""

    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            _copy_traversable(child, target)
        else:
            with child.open("rb") as input_stream, target.open("wb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)


@contextmanager
def resource_directory(relative: str | Path) -> Iterator[Path]:
    """Yield a copyable resource directory from a checkout or installed wheel."""

    requested = Path(relative)
    checkout_path = Path(__file__).resolve().parents[2] / requested
    if checkout_path.is_dir():
        yield checkout_path
        return

    resource = files("econ_manim").joinpath("_resources", *requested.parts)
    if not resource.is_dir():
        raise ConfigError(f"bundled resource does not exist: {requested.as_posix()}")

    try:
        direct_path = Path(resource)
    except TypeError:
        direct_path = None
    if direct_path is not None and direct_path.is_dir():
        yield direct_path
        return

    with TemporaryDirectory(prefix="econ-manim-resource-") as temporary:
        materialized = Path(temporary) / requested.name
        _copy_traversable(resource, materialized)
        yield materialized
