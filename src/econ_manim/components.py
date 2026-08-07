"""Minimal, symmetric objects for economic agents, choices, and markets."""

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
    Rectangle,
    RoundedRectangle,
    VGroup,
)

from .theme import ECON_DARK, VideoTheme
from .typography import ProseText as Text
from .typography import fit_prose_text


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


class AgentToken(VGroup):
    """A domain-neutral token for a household, firm, person, or institution."""

    def __init__(
        self,
        *,
        color: str | None = None,
        label: str | None = None,
        scale: float = 1.0,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        token_color = color or theme.foreground
        boundary = Circle(
            radius=0.22,
            stroke_color=token_color,
            stroke_width=1.8,
            fill_color=theme.card,
            fill_opacity=1,
        )
        core = Dot(radius=0.065, color=token_color)
        symbol = VGroup(boundary, core)
        parts = [symbol]
        if label:
            label_mobject = Text(label, font_size=18, color=token_color)
            label_mobject.next_to(symbol, DOWN, buff=0.12)
            parts.append(label_mobject)
        super().__init__(*parts)
        self.symbol = symbol
        self.scale(scale)


class ChoiceMap(VGroup):
    """A compact fan from one economic agent to two-to-four named alternatives."""

    def __init__(
        self,
        choices: Sequence[tuple[str, str]],
        *,
        agent_label: str = "agent",
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not 2 <= len(choices) <= 4:
            raise ValueError("a choice map requires between two and four alternatives")

        origin = AgentToken(label=agent_label, color=theme.foreground, theme=theme)
        origin.move_to(LEFT * 3.15)
        nodes = VGroup()
        labels = VGroup()
        for label, color in choices:
            node = RoundedRectangle(
                width=2.30,
                height=0.62,
                corner_radius=0.12,
                stroke_color=color,
                stroke_width=1.6,
                fill_color=theme.card,
                fill_opacity=0.96,
            )
            text = fit_prose_text(
                label,
                max_width=1.92,
                font_size=20,
                min_font_size=12,
                color=color,
            )
            text.move_to(node)
            nodes.add(node)
            labels.add(text)
        node_rows = VGroup(
            *[VGroup(node, label) for node, label in zip(nodes, labels, strict=True)]
        )
        node_rows.arrange(DOWN, buff=0.24).move_to(RIGHT * 1.55)

        routes = VGroup()
        for node in nodes:
            routes.add(
                Arrow(
                    origin.symbol.get_right(),
                    node.get_left(),
                    buff=0.12,
                    color=node.get_stroke_color(),
                    stroke_width=2.0,
                    tip_length=0.13,
                )
            )

        super().__init__(origin, routes, node_rows)
        self.origin = origin
        self.routes = routes
        self.nodes = nodes
        self.labels = labels


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
        self.theme = theme

    def shock_cell(self, index: int = 0, *, color: str | None = None) -> RoundedRectangle:
        """Return a highlighted copy of a sector cell for shock animations."""

        target = self.cells[index].copy()
        target.set_fill(color or self.theme.orange, opacity=0.95)
        target.set_stroke(color or self.theme.orange, width=2.4)
        return target


class PaperCodeEndSlate(VGroup):
    """A restrained final card linking a paper and its reusable code package."""

    def __init__(
        self,
        *,
        paper_title: str,
        paper_authors: str,
        paper_status: str,
        package_name: str,
        package_summary: str,
        package_url: str,
        package_status: str = "Package available now",
        invitation: str = "Apply the method to your own setting.",
        paper_heading: str = "Paper",
        package_heading: str = "Code and practitioner guide",
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        required = {
            "paper_title": paper_title,
            "paper_authors": paper_authors,
            "paper_status": paper_status,
            "package_name": package_name,
            "package_summary": package_summary,
            "package_url": package_url,
        }
        if any(not value.strip() for value in required.values()):
            raise ValueError("paper and package resource fields cannot be empty")

        paper_outline = Rectangle(
            width=0.95,
            height=1.20,
            color=theme.blue,
            stroke_width=2.2,
        ).set_fill(theme.background, opacity=1.0)
        paper_lines = VGroup(
            *[
                Line(
                    [-0.30, y_position, 0],
                    [0.30, y_position, 0],
                    color=theme.blue,
                    stroke_width=1.4,
                ).set_stroke(opacity=0.70)
                for y_position in (0.25, 0.02, -0.21)
            ]
        )
        paper_icon = VGroup(paper_outline, paper_lines)
        paper_title_mobject = fit_prose_text(
            paper_title,
            max_width=5.10,
            font_size=21,
            min_font_size=14,
            color=theme.foreground,
            weight="BOLD",
            line_spacing=1.05,
        )
        paper_resource = VGroup(
            paper_icon,
            Text(
                paper_heading,
                font_size=22,
                color=theme.blue,
                weight="BOLD",
            ),
            paper_title_mobject,
            Text(paper_authors, font_size=17, color=theme.muted),
            Text(
                paper_status,
                font_size=18,
                color=theme.blue,
                weight="BOLD",
                line_spacing=1.05,
            ),
        ).arrange(DOWN, buff=0.20).move_to([-3.25, 0.18, 0])

        code_outline = Rectangle(
            width=1.35,
            height=1.00,
            color=theme.green,
            stroke_width=2.2,
        ).set_fill(theme.background, opacity=1.0)
        code_symbol = Text(
            "{  }",
            font_size=30,
            color=theme.green,
            weight="BOLD",
        ).move_to(code_outline)
        display_url = package_url
        if "\n" not in display_url and len(display_url) > 34 and "/" in display_url:
            prefix, suffix = display_url.rsplit("/", 1)
            display_url = f"{prefix}/\n{suffix}"
        code_resource = VGroup(
            VGroup(code_outline, code_symbol),
            Text(
                package_heading,
                font_size=22,
                color=theme.green,
                weight="BOLD",
            ),
            fit_prose_text(
                package_name,
                max_width=5.10,
                font_size=21,
                min_font_size=14,
                color=theme.foreground,
                weight="BOLD",
            ),
            Text(
                package_summary,
                font_size=18,
                color=theme.foreground,
                line_spacing=1.05,
            ),
            Text(
                display_url,
                font_size=15,
                color=theme.muted,
                line_spacing=1.05,
            ),
            Text(
                package_status,
                font_size=18,
                color=theme.green,
                weight="BOLD",
            ),
        ).arrange(DOWN, buff=0.18).move_to([3.25, 0.18, 0])

        divider = Line(
            [0, -2.15, 0],
            [0, 2.15, 0],
            color=theme.grid,
            stroke_width=1.2,
        )
        invitation_mobject = Text(
            invitation,
            font_size=20,
            color=theme.foreground,
        ).move_to([0, -2.62, 0])

        super().__init__(paper_resource, divider, code_resource, invitation_mobject)
        self.paper_resource = paper_resource
        self.divider = divider
        self.code_resource = code_resource
        self.invitation = invitation_mobject


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
