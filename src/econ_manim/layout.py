"""Small layout assertions used by tests and scene-level QA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Positioned(Protocol):
    def get_left(self): ...

    def get_right(self): ...

    def get_top(self): ...

    def get_bottom(self): ...


class LayoutError(ValueError):
    """Raised when declared scene geometry violates a layout invariant."""


@dataclass(frozen=True, slots=True)
class Bounds:
    left: float
    right: float
    bottom: float
    top: float


def bounds_of(mobject: Positioned) -> Bounds:
    """Return axis-aligned scene bounds for a Manim mobject."""

    return Bounds(
        left=float(mobject.get_left()[0]),
        right=float(mobject.get_right()[0]),
        bottom=float(mobject.get_bottom()[1]),
        top=float(mobject.get_top()[1]),
    )


def assert_within_frame(
    mobject: Positioned,
    *,
    x_limit: float = 6.70,
    y_limit: float = 3.65,
    name: str = "mobject",
) -> None:
    """Reject objects that extend outside the title-safe content frame."""

    box = bounds_of(mobject)
    if box.left < -x_limit or box.right > x_limit or box.bottom < -y_limit or box.top > y_limit:
        raise LayoutError(
            f"{name} is outside the safe frame: "
            f"({box.left:.2f}, {box.right:.2f}, {box.bottom:.2f}, {box.top:.2f})"
        )


def assert_no_overlap(
    first: Positioned,
    second: Positioned,
    *,
    buffer: float = 0.05,
    names: tuple[str, str] = ("first", "second"),
) -> None:
    """Reject an axis-aligned overlap between two declared layout regions."""

    a = bounds_of(first)
    b = bounds_of(second)
    separated = (
        a.right + buffer <= b.left
        or b.right + buffer <= a.left
        or a.top + buffer <= b.bottom
        or b.top + buffer <= a.bottom
    )
    if not separated:
        raise LayoutError(f"{names[0]} overlaps {names[1]}")
