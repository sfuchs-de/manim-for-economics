"""Minimal, symmetric objects for workers, cities, and adjustment margins."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    CurvedArrow,
    Dot,
    Line,
    RoundedRectangle,
    Text,
    VGroup,
)

from .theme import ECON_DARK, VideoTheme


class WorkerToken(VGroup):
    """A compact worker glyph that remains legible at presentation scale."""

    def __init__(
        self,
        *,
        color: str | None = None,
        label: str | None = None,
        scale: float = 1.0,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        worker_color = color or theme.foreground
        head = Circle(radius=0.09, stroke_width=0, fill_color=worker_color, fill_opacity=1)
        body = RoundedRectangle(
            width=0.20,
            height=0.25,
            corner_radius=0.07,
            stroke_width=0,
            fill_color=worker_color,
            fill_opacity=1,
        ).next_to(head, DOWN, buff=0.035)
        glyph = VGroup(head, body)
        parts = [glyph]
        if label:
            label_mobject = Text(label, font_size=18, color=worker_color)
            label_mobject.next_to(glyph, DOWN, buff=0.11)
            parts.append(label_mobject)
        super().__init__(*parts)
        self.scale(scale)


class CityLaborMarket(VGroup):
    """A circular city containing four symmetric sector-occupation cells."""

    CELL_OFFSETS = (
        np.array([-0.52, 0.40, 0.0]),
        np.array([0.52, 0.40, 0.0]),
        np.array([-0.52, -0.40, 0.0]),
        np.array([0.52, -0.40, 0.0]),
    )

    def __init__(
        self,
        name: str,
        workers_per_cell: Sequence[int] = (2, 2, 2, 2),
        *,
        radius: float = 1.45,
        accent: str | None = None,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if len(workers_per_cell) != 4:
            raise ValueError("workers_per_cell must contain four values")
        if any(count < 0 or count > 6 for count in workers_per_cell):
            raise ValueError("each cell must contain between zero and six workers")

        city_color = accent or theme.green
        boundary = Circle(radius=radius, color=city_color, stroke_width=2.2)
        title = Text(name, font_size=24, color=city_color)
        title.next_to(boundary, UP, buff=0.18)

        cells = VGroup()
        worker_groups = VGroup()
        palette = (theme.blue, theme.green, theme.orange, theme.rose)
        for index, (offset, count) in enumerate(
            zip(self.CELL_OFFSETS, workers_per_cell, strict=True)
        ):
            cell = RoundedRectangle(
                width=0.86,
                height=0.62,
                corner_radius=0.12,
                stroke_color=palette[index],
                stroke_width=1.5,
                fill_color=theme.card,
                fill_opacity=0.92,
            ).move_to(offset)
            workers = VGroup()
            positions = (
                (-0.22, 0.13),
                (0.0, 0.13),
                (0.22, 0.13),
                (-0.22, -0.13),
                (0.0, -0.13),
                (0.22, -0.13),
            )
            for x, y in positions[:count]:
                workers.add(
                    Dot(
                        cell.get_center() + np.array([x, y, 0]),
                        radius=0.045,
                        color=theme.foreground,
                    )
                )
            cells.add(cell)
            worker_groups.add(workers)

        inner_cross = VGroup(
            Line(UP * 0.08, DOWN * 0.08, color=theme.grid, stroke_width=1),
            Line(LEFT * 0.08, RIGHT * 0.08, color=theme.grid, stroke_width=1),
        )
        super().__init__(boundary, cells, worker_groups, inner_cross, title)
        self.boundary = boundary
        self.cells = cells
        self.workers = worker_groups
        self.title = title
        self.radius = radius

    def shock_cell(self, index: int = 0, *, color: str | None = None) -> RoundedRectangle:
        """Return a highlighted copy of a sector cell for shock animations."""

        target = self.cells[index].copy()
        target.set_fill(color or ECON_DARK.orange, opacity=0.95)
        target.set_stroke(color or ECON_DARK.orange, width=2.4)
        return target


def adjustment_route(
    start,
    end,
    *,
    label: str,
    color: str,
    curved: bool = False,
    label_direction=UP,
) -> VGroup:
    """Create a restrained arrow and direct label for an adjustment margin."""

    arrow = (
        CurvedArrow(start, end, angle=-0.25, color=color, stroke_width=2.6, tip_length=0.15)
        if curved
        else Arrow(start, end, buff=0.12, color=color, stroke_width=2.6, tip_length=0.15)
    )
    text = Text(label, font_size=20, color=color)
    text.next_to(arrow.get_center(), label_direction, buff=0.12)
    return VGroup(arrow, text)
