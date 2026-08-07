"""Reusable visual formats for mechanism-led economics explainers."""

from __future__ import annotations

from collections.abc import Sequence

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Line,
    Rectangle,
    RoundedRectangle,
    VGroup,
)

from .theme import ECON_DARK, VideoTheme
from .typography import ProseText as Text
from .typography import fit_prose_text


class CausalChain(VGroup):
    """A direct-label chain that can be built one economic link at a time."""

    def __init__(
        self,
        steps: Sequence[tuple[str, str]],
        *,
        font_size: int = 26,
        max_width: float = 12.2,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if len(steps) < 2:
            raise ValueError("a causal chain requires at least two steps")

        nodes = VGroup(
            *[
                Text(label, font_size=font_size, color=color)
                for label, color in steps
            ]
        )
        arrows = VGroup(
            *[
                Arrow(
                    LEFT * 0.28,
                    RIGHT * 0.28,
                    buff=0,
                    color=theme.muted,
                    stroke_width=1.8,
                    tip_length=0.12,
                )
                for _ in range(len(nodes) - 1)
            ]
        )
        sequence = VGroup()
        for index, node in enumerate(nodes):
            if index:
                sequence.add(arrows[index - 1])
            sequence.add(node)
        sequence.arrange(RIGHT, buff=0.18)
        if sequence.width > max_width:
            sequence.scale_to_fit_width(max_width)

        super().__init__(sequence)
        self.nodes = nodes
        self.arrows = arrows
        self.sequence = sequence


class LinkedViews(VGroup):
    """Place two representations of the same economic state on a shared stage."""

    def __init__(
        self,
        left_view,
        right_view,
        *,
        left_title: str,
        right_title: str,
        relation: str = "same economic state",
        max_view_width: float = 4.8,
        max_view_height: float = 3.25,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        for view in (left_view, right_view):
            if view.width > max_view_width:
                view.scale_to_fit_width(max_view_width)
            if view.height > max_view_height:
                view.scale_to_fit_height(max_view_height)

        left_heading = Text(
            left_title,
            font_size=22,
            color=theme.foreground,
            weight="BOLD",
        )
        right_heading = Text(
            right_title,
            font_size=22,
            color=theme.foreground,
            weight="BOLD",
        )
        left_group = VGroup(left_heading, left_view).arrange(DOWN, buff=0.24)
        right_group = VGroup(right_heading, right_view).arrange(DOWN, buff=0.24)
        views = VGroup(left_group, right_group).arrange(
            RIGHT,
            buff=1.20,
            aligned_edge=UP,
        )

        relation_label = Text(relation, font_size=18, color=theme.muted)
        relation_y = min(
            left_group.get_bottom()[1],
            right_group.get_bottom()[1],
        ) - 0.18
        relation_rule = Line(
            [left_group.get_left()[0], relation_y, 0],
            [right_group.get_right()[0], relation_y, 0],
            color=theme.grid,
            stroke_width=1.0,
        )
        relation_label.move_to(relation_rule)
        relation_label.add_background_rectangle(
            color=theme.background,
            opacity=1,
            buff=0.12,
        )
        relation_group = VGroup(relation_rule, relation_label)
        relation_group.next_to(views, DOWN, buff=0.28)

        super().__init__(views, relation_group)
        self.left_view = left_view
        self.right_view = right_view
        self.left_group = left_group
        self.right_group = right_group
        self.headings = VGroup(left_heading, right_heading)
        self.relation = relation_group


class DivergingBarChart(VGroup):
    """Compare results with a benchmark using a stable, directly labeled zero line."""

    def __init__(
        self,
        rows: Sequence[tuple[str, float, str]],
        *,
        benchmark_label: str = "benchmark",
        left_label: str = "smaller",
        right_label: str = "larger",
        value_format: str = "{:+.0f}%",
        plot_half_width: float = 2.55,
        row_gap: float = 0.72,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not rows:
            raise ValueError("a diverging bar chart requires at least one row")

        maximum = max(abs(float(value)) for _, value, _ in rows)
        if maximum == 0:
            maximum = 1.0
        top_y = row_gap * (len(rows) - 1) / 2
        bottom_y = -top_y

        zero = Line(
            [0, top_y + 0.48, 0],
            [0, bottom_y - 0.48, 0],
            color=theme.muted,
            stroke_width=1.6,
        )
        benchmark = Text(benchmark_label, font_size=17, color=theme.muted)
        benchmark.next_to(zero, UP, buff=0.10)
        side_labels = VGroup(
            Text(left_label, font_size=17, color=theme.muted).move_to(
                [-plot_half_width * 0.72, top_y + 0.72, 0]
            ),
            Text(right_label, font_size=17, color=theme.muted).move_to(
                [plot_half_width * 0.72, top_y + 0.72, 0]
            ),
        )

        row_groups = VGroup()
        labels = VGroup()
        bars = VGroup()
        values = VGroup()
        for index, (label, value, color) in enumerate(rows):
            y = top_y - index * row_gap
            numeric_value = float(value)
            width = max(abs(numeric_value) / maximum * plot_half_width, 0.015)
            bar = Rectangle(
                width=width,
                height=0.28,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.92 if numeric_value else 0.35,
            )
            direction = 1 if numeric_value >= 0 else -1
            bar.move_to([direction * width / 2, y, 0])

            row_label = Text(label, font_size=19, color=theme.foreground)
            label_anchor = -plot_half_width - 1.30
            row_label.move_to([label_anchor, y, 0])
            row_label.align_to([label_anchor, y, 0], RIGHT)

            amount = Text(
                value_format.format(numeric_value),
                font_size=19,
                color=color,
            )
            amount.next_to(bar, RIGHT if numeric_value >= 0 else LEFT, buff=0.12)

            row = VGroup(row_label, bar, amount)
            row_groups.add(row)
            labels.add(row_label)
            bars.add(bar)
            values.add(amount)

        chart = VGroup(zero, benchmark, side_labels, row_groups)
        if chart.width > 11.8:
            chart.scale_to_fit_width(11.8)
        super().__init__(chart)
        self.zero = zero
        self.benchmark = benchmark
        self.side_labels = side_labels
        self.rows = row_groups
        self.labels = labels
        self.bars = bars
        self.values = values


class ChannelDecomposition(VGroup):
    """Connect named economic channels to one common outcome."""

    def __init__(
        self,
        channels: Sequence[tuple[str, str]],
        *,
        outcome: str = "outcome",
        outcome_color: str | None = None,
        max_channels: int = 4,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not 2 <= len(channels) <= max_channels:
            raise ValueError(
                f"a channel decomposition requires between two and {max_channels} channels"
            )

        channel_groups = VGroup()
        for label, color in channels:
            text = fit_prose_text(
                label,
                max_width=2.45,
                font_size=20,
                min_font_size=12,
                color=color,
            )
            box = RoundedRectangle(
                width=2.85,
                height=0.62,
                corner_radius=0.11,
                stroke_color=color,
                stroke_width=1.5,
                fill_color=theme.card,
                fill_opacity=0.94,
            )
            text.move_to(box)
            channel_groups.add(VGroup(box, text))
        channel_groups.arrange(DOWN, buff=0.28).move_to(LEFT * 2.45)

        resolved_outcome_color = outcome_color or theme.foreground
        outcome_text = fit_prose_text(
            outcome,
            max_width=2.55,
            font_size=23,
            min_font_size=12,
            color=resolved_outcome_color,
        )
        outcome_box = RoundedRectangle(
            width=3.05,
            height=0.86,
            corner_radius=0.14,
            stroke_color=resolved_outcome_color,
            stroke_width=1.8,
            fill_color=theme.card,
            fill_opacity=0.96,
        )
        outcome_text.move_to(outcome_box)
        outcome_group = VGroup(outcome_box, outcome_text).move_to(RIGHT * 2.45)

        arrows = VGroup()
        for channel, (_, color) in zip(channel_groups, channels, strict=True):
            arrows.add(
                Arrow(
                    channel.get_right(),
                    outcome_group.get_left(),
                    buff=0.13,
                    color=color,
                    stroke_width=2.0,
                    tip_length=0.13,
                )
            )

        super().__init__(channel_groups, arrows, outcome_group)
        self.channels = channel_groups
        self.arrows = arrows
        self.outcome = outcome_group
