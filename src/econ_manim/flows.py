"""Reusable paths for showing movement through an economic system."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from manim import (
    UP,
    ArcBetweenPoints,
    Arrow,
    Dot,
    MoveAlongPath,
    TipableVMobject,
    VGroup,
    linear,
)

from .theme import ECON_DARK, VideoTheme
from .typography import ProseText as Text


class PathFlow(VGroup):
    """A labeled route with an exposed token and travel animation.

    Two points create a straight route by default. Set ``curved=True`` for an
    arc, or supply three or more points for a multi-segment route.
    """

    def __init__(
        self,
        points: Sequence[Sequence[float]],
        *,
        label: str = "",
        color: str | None = None,
        curved: bool = False,
        bend: float = 0.32,
        token=None,
        label_direction=UP,
        label_buff: float = 0.12,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if len(points) < 2:
            raise ValueError("a path flow requires at least two points")
        coordinates = tuple(np.asarray(point, dtype=float) for point in points)
        if any(point.shape != (3,) for point in coordinates):
            raise ValueError("each path point must contain x, y, and z coordinates")
        route_color = color or theme.blue

        if len(coordinates) == 2 and not curved:
            path = Arrow(
                coordinates[0],
                coordinates[1],
                buff=0,
                color=route_color,
                stroke_width=2.6,
                tip_length=0.14,
            )
        elif len(coordinates) == 2:
            path = ArcBetweenPoints(
                coordinates[0],
                coordinates[1],
                angle=bend,
                color=route_color,
                stroke_width=2.6,
            )
            path.add_tip(tip_length=0.14)
        else:
            path = TipableVMobject(color=route_color, stroke_width=2.6)
            if curved:
                path.set_points_smoothly(coordinates)
            else:
                path.set_points_as_corners(coordinates)
            path.add_tip(tip_length=0.14)

        moving_token = token or Dot(radius=0.075, color=route_color)
        moving_token.move_to(path.get_start())
        label_mobject = Text(label, font_size=18, color=route_color) if label else VGroup()
        if label:
            label_mobject.next_to(
                path.point_from_proportion(0.5),
                label_direction,
                buff=label_buff,
            )

        super().__init__(path, label_mobject, moving_token)
        self.path = path
        self.label = label_mobject
        self.token = moving_token

    def travel_animation(self, *, run_time: float = 1.0):
        """Return a deterministic animation that moves the token along the path."""

        if run_time <= 0:
            raise ValueError("run_time must be positive")
        return MoveAlongPath(
            self.token,
            self.path,
            run_time=run_time,
            rate_func=linear,
        )
