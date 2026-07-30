"""Economics-native charts with stable axes and direct labeling."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Dot,
    Line,
    MathTex,
    RoundedRectangle,
    Text,
    VGroup,
    VMobject,
)

from .theme import ECON_DARK, VideoTheme


def _line(axes: Axes, values: Sequence[float], color: str, width: float = 3.2) -> VMobject:
    path = VMobject(color=color, stroke_width=width)
    points = [axes.c2p(index, float(value)) for index, value in enumerate(values)]
    path.set_points_as_corners(points)
    return path


class ImpulseResponsePlot(VGroup):
    """A compact impulse-response chart with zero line and direct labels."""

    def __init__(
        self,
        series: Mapping[str, tuple[Sequence[float], str]],
        *,
        title: str = "",
        x_label: str = "quarters after shock",
        width: float = 5.5,
        height: float = 2.7,
        y_range: tuple[float, float, float] | None = None,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not series:
            raise ValueError("series cannot be empty")
        lengths = {len(values) for values, _ in series.values()}
        if len(lengths) != 1 or next(iter(lengths)) < 2:
            raise ValueError("all series must have the same length of at least two")
        length = next(iter(lengths))
        all_values = [float(value) for values, _ in series.values() for value in values]
        if y_range is None:
            lower = min(min(all_values), 0.0)
            upper = max(max(all_values), 0.0)
            span = max(upper - lower, 0.5)
            step = round(span / 4, 2)
            y_range = (lower - 0.12 * span, upper + 0.12 * span, step)

        axes = Axes(
            x_range=[0, length - 1, max(1, (length - 1) // 4)],
            y_range=list(y_range),
            x_length=width,
            y_length=height,
            tips=False,
            axis_config={"color": theme.grid, "stroke_width": 1.2, "include_ticks": True},
        )
        zero = Line(
            axes.c2p(0, 0),
            axes.c2p(length - 1, 0),
            color=theme.muted,
            stroke_width=1.0,
        )
        lines = VGroup()
        labels = VGroup()
        endpoints = []
        for name, (values, color) in series.items():
            curve = _line(axes, values, color)
            lines.add(curve)
            endpoints.append((float(values[-1]), curve, name, color))
        endpoints.sort(key=lambda item: item[0])
        for index, (_, curve, name, color) in enumerate(endpoints):
            label = Text(name, font_size=17, color=color)
            direction = DOWN if index == 0 else UP
            label.next_to(curve.get_end(), direction + LEFT, buff=0.08)
            labels.add(label)

        title_mobject = Text(title, font_size=23, color=theme.foreground) if title else VGroup()
        if title:
            title_mobject.next_to(axes, UP, buff=0.18)
        x_mobject = Text(x_label, font_size=16, color=theme.muted)
        x_mobject.next_to(axes, DOWN, buff=0.20)
        super().__init__(axes, zero, lines, labels, title_mobject, x_mobject)
        self.axes = axes
        self.zero = zero
        self.lines = lines
        self.labels = labels


class ShockDistribution(VGroup):
    """A one-dimensional dot distribution without decorative bars."""

    def __init__(
        self,
        observations: Sequence[tuple[float, str]],
        *,
        x_range: tuple[float, float, float] = (-1.5, 2.5, 0.5),
        width: float = 8.0,
        label: str = "realized local labor-demand shock",
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        from manim import NumberLine

        axis = NumberLine(
            x_range=list(x_range),
            length=width,
            color=theme.grid,
            stroke_width=1.5,
            include_numbers=True,
            font_size=18,
        )
        dots = VGroup()
        bin_counts: dict[int, int] = {}
        for value, color in observations:
            bin_id = int(round((value - x_range[0]) / 0.08))
            level = bin_counts.get(bin_id, 0)
            bin_counts[bin_id] = level + 1
            dot = Dot(
                axis.n2p(value) + UP * (0.14 + level * 0.13),
                radius=0.055,
                color=color,
            )
            dots.add(dot)
        axis_label = Text(label, font_size=18, color=theme.muted)
        axis_label.next_to(axis, DOWN, buff=0.32)
        super().__init__(axis, dots, axis_label)
        self.axis = axis
        self.dots = dots


class EquationBuild(VGroup):
    """A word-first additive decomposition designed for incremental reveals."""

    def __init__(
        self,
        terms: Sequence[tuple[str, str]],
        *,
        lhs: str = "worker welfare",
        operators: Sequence[str] | None = None,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not terms:
            raise ValueError("terms cannot be empty")
        operator_values = tuple(operators or ("+",) * (len(terms) - 1))
        if len(operator_values) != len(terms) - 1:
            raise ValueError("operators must contain one item between each pair of terms")
        lhs_mobject = Text(lhs, font_size=25, color=theme.foreground)
        equals = MathTex("=", font_size=34, color=theme.muted)
        term_groups = VGroup()
        operator_mobjects = VGroup()
        for index, (text, color) in enumerate(terms):
            label = Text(text, font_size=22, color=color)
            box = RoundedRectangle(
                width=label.width + 0.38,
                height=label.height + 0.28,
                corner_radius=0.10,
                stroke_color=color,
                stroke_width=1.4,
                fill_color=theme.card,
                fill_opacity=0.90,
            )
            label.move_to(box)
            term_groups.add(VGroup(box, label))
            if index:
                operator_mobjects.add(
                    MathTex(
                        operator_values[index - 1],
                        font_size=30,
                        color=theme.muted,
                    )
                )

        sequence = VGroup(lhs_mobject, equals)
        for index, term in enumerate(term_groups):
            if index:
                sequence.add(operator_mobjects[index - 1])
            sequence.add(term)
        sequence.arrange(RIGHT, buff=0.20)
        if sequence.width > 12.5:
            sequence.scale_to_fit_width(12.5)
        super().__init__(sequence)
        self.lhs = lhs_mobject
        self.equals = equals
        self.terms = term_groups
        self.operators = operator_mobjects
        self.sequence = sequence


class ResultTable(VGroup):
    """A small decomposition table with semantic numeric columns."""

    def __init__(
        self,
        headers: Sequence[tuple[str, str]],
        rows: Sequence[tuple[str, str, Sequence[float]]],
        *,
        number_format: str = "{:+.2f}%",
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not headers:
            raise ValueError("headers cannot be empty")
        if any(len(values) != len(headers) for _, _, values in rows):
            raise ValueError("each row must provide one value per header")

        label_width = 3.8
        column_width = 2.0
        header_group = VGroup()
        for index, (header, color) in enumerate(headers):
            mob = Text(header, font_size=19, color=color)
            mob.move_to([label_width / 2 + column_width * (index + 0.5), 0, 0])
            header_group.add(mob)

        row_groups = VGroup()
        for row_index, (label, label_color, values) in enumerate(rows):
            y = -(row_index + 1) * 0.78
            label_mobject = Text(label, font_size=20, color=label_color)
            label_mobject.move_to([-label_width / 2 + 0.10, y, 0])
            label_mobject.align_to([-label_width + 0.15, y, 0], LEFT)
            value_group = VGroup()
            for index, value in enumerate(values):
                value_mobject = Text(
                    number_format.format(value),
                    font_size=22 if index < len(values) - 1 else 25,
                    color=headers[index][1] if index < len(values) - 1 else theme.foreground,
                )
                value_mobject.move_to(
                    [label_width / 2 + column_width * (index + 0.5), y, 0]
                )
                value_group.add(value_mobject)
            row_groups.add(VGroup(label_mobject, value_group))

        rule = Line(
            [-label_width, -0.40, 0],
            [label_width / 2 + column_width * len(headers), -0.40, 0],
            color=theme.grid,
            stroke_width=1.0,
        )
        table = VGroup(header_group, rule, row_groups)
        table.move_to([0, 0, 0])
        super().__init__(table)
        self.headers = header_group
        self.rows = row_groups
        self.rule = rule
