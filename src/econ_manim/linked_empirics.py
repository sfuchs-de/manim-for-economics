"""Linked empirical views for model comparisons and spatial results."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Axes,
    DashedLine,
    Dot,
    Line,
    ManimColor,
    Rectangle,
    Transform,
    VectorizedPoint,
    VGroup,
    VMobject,
    interpolate_color,
)

from .theme import ECON_DARK, VideoTheme
from .typography import ProseText as Text
from .typography import fit_prose_text


@dataclass(frozen=True, slots=True)
class ScatterObservation:
    """One observation with a fixed benchmark and several model-based values."""

    identifier: str
    benchmark: float
    states: Mapping[str, float]
    label: str = ""


@dataclass(frozen=True, slots=True)
class NetworkLink:
    """A straight spatial link used by :class:`NetworkInset`."""

    identifier: str
    start: tuple[float, float]
    end: tuple[float, float]


@dataclass(frozen=True, slots=True)
class GeographicRegion:
    """A named geographic region represented by one or more exterior rings."""

    identifier: str
    rings: tuple[tuple[tuple[float, float], ...], ...]


def read_geojson_regions(
    path: str | Path,
    *,
    identifier_property: str = "GEOID",
) -> tuple[GeographicRegion, ...]:
    """Read Polygon and MultiPolygon exteriors from a local GeoJSON file."""

    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing GeoJSON file: {source}") from error
    if payload.get("type") != "FeatureCollection":
        raise ValueError("GeoJSON map data must be a FeatureCollection")

    regions: list[GeographicRegion] = []
    for index, feature in enumerate(payload.get("features", ())):
        properties = feature.get("properties") or {}
        identifier = properties.get(identifier_property)
        if identifier is None:
            raise ValueError(
                f"GeoJSON feature {index} lacks property {identifier_property!r}"
            )
        geometry = feature.get("geometry") or {}
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates") or ()
        if geometry_type == "Polygon":
            polygons = (coordinates,)
        elif geometry_type == "MultiPolygon":
            polygons = coordinates
        else:
            raise ValueError(f"unsupported GeoJSON geometry: {geometry_type!r}")

        rings = []
        for polygon in polygons:
            if not polygon:
                continue
            exterior = tuple((float(lon), float(lat)) for lon, lat, *_ in polygon[0])
            if len(exterior) >= 3:
                rings.append(exterior)
        if rings:
            regions.append(GeographicRegion(str(identifier), tuple(rings)))

    if not regions:
        raise ValueError("GeoJSON map data contains no polygon exteriors")
    identifiers = [region.identifier for region in regions]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("GeoJSON region identifiers must be unique")
    return tuple(regions)


def _sequential_color(value: float, colors: Sequence[str]) -> ManimColor:
    """Interpolate over a short perceptually ordered color sequence."""

    normalized = min(1.0, max(0.0, float(value)))
    scaled = normalized * (len(colors) - 1)
    lower = min(int(math.floor(scaled)), len(colors) - 2)
    fraction = scaled - lower
    return interpolate_color(
        ManimColor(colors[lower]),
        ManimColor(colors[lower + 1]),
        fraction,
    )


def _validate_observations(
    observations: Sequence[ScatterObservation],
    state_order: Sequence[str],
) -> None:
    if not observations:
        raise ValueError("an evolving scatter requires at least one observation")
    if not state_order:
        raise ValueError("state_order cannot be empty")
    identifiers = [observation.identifier for observation in observations]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("observation identifiers must be unique")
    required = set(state_order)
    for observation in observations:
        if not math.isfinite(float(observation.benchmark)):
            raise ValueError(f"nonfinite benchmark for {observation.identifier!r}")
        missing = required - set(observation.states)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(
                f"observation {observation.identifier!r} is missing states: {names}"
            )
        if any(not math.isfinite(float(observation.states[state])) for state in state_order):
            raise ValueError(f"nonfinite state value for {observation.identifier!r}")


def ranked_value_groups(
    values: Mapping[str, float],
    *,
    groups: int = 5,
    descending: bool = True,
) -> tuple[tuple[str, ...], ...]:
    """Split identifiers into deterministic, nearly equal rank groups.

    The function is intended for staged map and scatter reveals. It uses ranks,
    rather than estimated quantile cutoffs, so ties cannot create empty or
    unexpectedly large groups. Identifiers break exact ties deterministically.
    """

    if not values:
        raise ValueError("ranked value groups require at least one value")
    if groups <= 0:
        raise ValueError("groups must be positive")
    if groups > len(values):
        raise ValueError("groups cannot exceed the number of values")
    if any(not math.isfinite(float(value)) for value in values.values()):
        raise ValueError("ranked value groups require finite values")

    direction = -1.0 if descending else 1.0
    ordered = sorted(
        values,
        key=lambda identifier: (direction * float(values[identifier]), identifier),
    )
    base_size, remainder = divmod(len(ordered), groups)
    result: list[tuple[str, ...]] = []
    start = 0
    for index in range(groups):
        size = base_size + (1 if index < remainder else 0)
        result.append(tuple(ordered[start : start + size]))
        start += size
    return tuple(result)


def _rendered_opacity(mobject) -> float:
    """Return the opacity carried by a rendered leaf rather than its parent group."""

    for member in mobject.get_family()[1:]:
        fill_opacity = getattr(member, "fill_opacity", None)
        if fill_opacity is not None:
            return float(fill_opacity)
    return 1.0


class EvolvingScatterPlot(VGroup):
    """A benchmark scatter whose vertical coordinate moves across model states."""

    def __init__(
        self,
        observations: Sequence[ScatterObservation],
        state_order: Sequence[str],
        *,
        state_labels: Mapping[str, str] | None = None,
        initial_state: str | None = None,
        selected_colors: Mapping[str, str] | None = None,
        state_colors: Mapping[str, Mapping[str, str]] | None = None,
        x_range: tuple[float, float, float] = (0.0, 1.0, 0.25),
        y_range: tuple[float, float, float] | None = None,
        width: float = 7.2,
        height: float = 4.8,
        x_label: str = "Traditional approach",
        y_label: str = "Welfare gain",
        show_diagonal: bool = True,
        show_coordinates: bool = True,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        _validate_observations(observations, state_order)
        states = tuple(state_order)
        first_state = initial_state or states[0]
        if first_state not in states:
            raise ValueError("initial_state must appear in state_order")
        selected = dict(selected_colors or {})
        unknown = set(selected) - {observation.identifier for observation in observations}
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"selected observations are absent from the scatter: {names}")
        encoded_colors = {
            state: dict(colors) for state, colors in (state_colors or {}).items()
        }
        unknown_states = set(encoded_colors) - set(states)
        if unknown_states:
            names = ", ".join(sorted(unknown_states))
            raise ValueError(f"scatter colors contain unknown states: {names}")
        observation_ids = {observation.identifier for observation in observations}
        for state, colors in encoded_colors.items():
            if set(colors) != observation_ids:
                raise ValueError(
                    f"scatter colors for {state!r} must cover every observation"
                )

        axes = Axes(
            x_range=list(x_range),
            y_range=list(y_range or x_range),
            x_length=width,
            y_length=height,
            tips=False,
            axis_config={
                "color": theme.grid,
                "stroke_width": 1.15,
                "include_ticks": True,
            },
        )
        if show_coordinates:
            axes.add_coordinates(
                font_size=14,
                num_decimal_places=2,
                color=theme.muted,
            )
        diagonal = (
            Line(
                axes.c2p(x_range[0], x_range[0]),
                axes.c2p(x_range[1], x_range[1]),
                color=theme.muted,
                stroke_width=1.2,
            ).set_stroke(opacity=0.62)
            if show_diagonal
            else VGroup()
        )

        dots = VGroup()
        point_color = theme.muted
        for observation in observations:
            color = encoded_colors.get(first_state, {}).get(
                observation.identifier,
                point_color,
            )
            radius = 0.070 if observation.identifier in selected else 0.034
            dot = Dot(
                axes.c2p(
                    float(observation.benchmark),
                    float(observation.states[first_state]),
                ),
                radius=radius,
                color=color,
                fill_opacity=0.88 if observation.identifier in selected else 0.66,
            )
            if observation.identifier in selected:
                dot.set_stroke(
                    selected[observation.identifier],
                    width=2.2,
                    opacity=1.0,
                )
            else:
                dot.set_stroke(color, width=0.45, opacity=0.78)
            dots.add(dot)

        x_text = Text(x_label, font_size=17, color=theme.foreground)
        x_text.next_to(axes, DOWN, buff=0.26)
        y_text = Text(y_label, font_size=17, color=theme.foreground).rotate(PI / 2)
        y_text.next_to(axes, LEFT, buff=0.30)
        labels = dict(state_labels or {})
        state_text = Text(
            labels.get(first_state, first_state),
            font_size=21,
            color=theme.foreground,
        )
        state_text.next_to(axes, UP, buff=0.16)

        super().__init__(axes, diagonal, dots, x_text, y_text, state_text)
        self.axes = axes
        self.diagonal = diagonal
        self.dots = dots
        self.x_label = x_text
        self.y_label = y_text
        self.state_label = state_text
        self.observations = tuple(observations)
        self.state_order = states
        self.state_labels = labels
        self.selected_colors = selected
        self.state_colors = encoded_colors
        self.current_state = first_state
        self._theme = theme
        self.dots_by_id = {
            observation.identifier: dot
            for observation, dot in zip(self.observations, self.dots, strict=True)
        }

    def point(self, identifier: str, state: str | None = None) -> np.ndarray:
        """Return an observation's plotted point in the requested state."""

        selected_state = state or self.current_state
        for observation in self.observations:
            if observation.identifier == identifier:
                return self.axes.c2p(
                    float(observation.benchmark),
                    float(observation.states[selected_state]),
                )
        raise KeyError(identifier)

    def ranks(self, state: str) -> dict[str, int]:
        """Return descending ranks, with identifiers breaking exact ties."""

        ordered = sorted(
            self.observations,
            key=lambda observation: (
                -float(observation.states[state]),
                observation.identifier,
            ),
        )
        return {observation.identifier: index + 1 for index, observation in enumerate(ordered)}

    def dot_layers(self, identifiers: Sequence[str]) -> VGroup:
        """Return existing dots in the requested deterministic reveal order."""

        chosen = tuple(identifiers)
        if len(chosen) != len(set(chosen)):
            raise ValueError("scatter layer identifiers must be unique")
        unknown = set(chosen) - set(self.dots_by_id)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"scatter layer contains unknown observations: {names}")
        return VGroup(*(self.dots_by_id[identifier] for identifier in chosen))

    def transition_lines(
        self,
        next_state: str,
        *,
        identifiers: Sequence[str] | None = None,
        opacity: float = 0.68,
    ) -> VGroup:
        """Connect selected observations' current and next positions."""

        if next_state not in self.state_order:
            raise KeyError(next_state)
        chosen = tuple(identifiers or self.selected_colors)
        lines = VGroup()
        for identifier in chosen:
            lines.add(
                Line(
                    self.point(identifier, self.current_state),
                    self.point(identifier, next_state),
                    color=self.selected_colors.get(identifier, self.theme.muted),
                    stroke_width=1.6,
                ).set_stroke(opacity=opacity)
            )
        return lines

    @property
    def theme(self) -> VideoTheme:
        """Infer the theme retained by this component."""

        return self._theme

    @theme.setter
    def theme(self, value: VideoTheme) -> None:
        self._theme = value

    def animate_to(self, state: str, *, run_time: float = 1.6) -> AnimationGroup:
        """Move the same observations to a new vertical model-based value."""

        if state not in self.state_order:
            raise KeyError(state)
        target_dots = self.dots.copy()
        for observation, dot in zip(self.observations, target_dots, strict=True):
            dot.move_to(
                self.axes.c2p(
                    float(observation.benchmark),
                    float(observation.states[state]),
                )
            )
            color = self.state_colors.get(state, {}).get(
                observation.identifier,
                self._theme.muted,
            )
            dot.set_fill(
                color,
                opacity=0.88 if observation.identifier in self.selected_colors else 0.66,
            )
            if observation.identifier in self.selected_colors:
                dot.set_stroke(
                    self.selected_colors[observation.identifier],
                    width=2.2,
                    opacity=1.0,
                )
            else:
                dot.set_stroke(color, width=0.45, opacity=0.78)
        target_label = Text(
            self.state_labels.get(state, state),
            font_size=21,
            color=self._theme.foreground,
        ).move_to(self.state_label)
        target_label.set_opacity(_rendered_opacity(self.state_label))
        animation = AnimationGroup(
            Transform(self.dots, target_dots),
            Transform(self.state_label, target_label),
            lag_ratio=0,
            run_time=run_time,
        )
        self.current_state = state
        return animation


class SelectedRankProjections(VGroup):
    """Project selected scatter observations onto the welfare axis with ranks."""

    def __init__(
        self,
        scatter: EvolvingScatterPlot,
        identifiers: Sequence[str] | None = None,
        *,
        initial_state: str | None = None,
        line_opacity: float = 0.42,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        chosen = tuple(identifiers or scatter.selected_colors)
        if not chosen:
            raise ValueError("rank projections require at least one observation")
        unknown = set(chosen) - set(scatter.dots_by_id)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(
                f"rank-projection observations are absent from the scatter: {names}"
            )
        state = initial_state or scatter.current_state
        if state not in scatter.state_order:
            raise KeyError(state)
        self.scatter = scatter
        self.identifiers = chosen
        self.line_opacity = float(line_opacity)
        self._theme = theme
        projections = self._build(state)
        super().__init__(*projections)
        self.current_state = state

    def _build(self, state: str) -> VGroup:
        ranks = self.scatter.ranks(state)
        x_min = float(self.scatter.axes.x_range[0])
        projections = VGroup()
        for identifier in self.identifiers:
            point = self.scatter.point(identifier, state)
            axis_point = self.scatter.axes.c2p(
                x_min,
                float(self.scatter.axes.p2c(point)[1]),
            )
            color = self.scatter.selected_colors.get(identifier, self._theme.foreground)
            line = DashedLine(
                axis_point + RIGHT * 0.08,
                point,
                dash_length=0.09,
                dashed_ratio=0.56,
                color=color,
                stroke_width=1.25,
            ).set_stroke(opacity=self.line_opacity)
            marker = Dot(
                axis_point,
                radius=0.043,
                color=color,
                fill_opacity=0.96,
            ).set_stroke(self._theme.background, width=1.2, opacity=1.0)
            rank = Text(
                f"#{ranks[identifier]}",
                font_size=13,
                color=color,
                weight="BOLD",
            ).next_to(marker, RIGHT, buff=0.07).shift(UP * 0.11)
            projections.add(VGroup(line, marker, rank))
        return projections

    def animate_to(self, state: str, *, run_time: float = 1.6) -> AnimationGroup:
        """Move each projection and rank label to a new welfare state."""

        if state not in self.scatter.state_order:
            raise KeyError(state)
        target = self._build(state)
        animation = AnimationGroup(
            Transform(self, target),
            lag_ratio=0,
            run_time=run_time,
        )
        self.current_state = state
        return animation


class SelectedRankPanel(VGroup):
    """Ranks for selected observations, updated from the same scatter states."""

    def __init__(
        self,
        scatter: EvolvingScatterPlot,
        labels: Mapping[str, str],
        *,
        initial_state: str | None = None,
        width: float = 4.25,
        name_font_size: float = 17,
        rank_font_size: float = 18,
        state_font_size: float = 16,
        row_spacing: float = 0.18,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not labels:
            raise ValueError("a rank panel requires at least one selected observation")
        unknown = set(labels) - set(scatter.dots_by_id)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"rank-panel observations are absent from the scatter: {names}")
        state = initial_state or scatter.current_state
        ranks = scatter.ranks(state)
        rows = VGroup()
        rank_labels = VGroup()
        name_labels = VGroup()
        for identifier, label in labels.items():
            rank = Text(
                f"#{ranks[identifier]}",
                font_size=rank_font_size,
                color=theme.foreground,
            )
            name = fit_prose_text(
                label,
                max_width=max(2.3, width - rank.width - 0.25),
                font_size=name_font_size,
                min_font_size=12,
                color=scatter.selected_colors[identifier],
            )
            row = VGroup(name, rank).arrange(RIGHT, buff=0.25)
            rows.add(row)
            name_labels.add(name)
            rank_labels.add(rank)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=row_spacing)
        state_label = Text(
            scatter.state_labels.get(state, state),
            font_size=state_font_size,
            color=theme.muted,
        )
        state_label.next_to(rows, UP, aligned_edge=LEFT, buff=0.18)
        super().__init__(state_label, rows)
        self.scatter = scatter
        self.identifiers = tuple(labels)
        self.rows = rows
        self.rank_labels = rank_labels
        self.name_labels = name_labels
        self.state_label = state_label
        self.current_state = state
        self._theme = theme
        self._rank_font_size = rank_font_size
        self._state_font_size = state_font_size

    def animate_to(self, state: str, *, run_time: float = 0.7) -> AnimationGroup:
        """Update the displayed ranks after a scatter transition."""

        ranks = self.scatter.ranks(state)
        target_ranks = self.rank_labels.copy()
        for identifier, label in zip(self.identifiers, target_ranks, strict=True):
            replacement = Text(
                f"#{ranks[identifier]}",
                font_size=self._rank_font_size,
                color=self._theme.foreground,
            ).move_to(label)
            replacement.set_opacity(_rendered_opacity(label))
            label.become(replacement)
        target_state = Text(
            self.scatter.state_labels.get(state, state),
            font_size=self._state_font_size,
            color=self._theme.muted,
        ).move_to(self.state_label)
        target_state.set_opacity(_rendered_opacity(self.state_label))
        self.current_state = state
        return AnimationGroup(
            Transform(self.rank_labels, target_ranks),
            Transform(self.state_label, target_state),
            lag_ratio=0,
            run_time=run_time,
        )


class SelectedRankHistoryPanel(VGroup):
    """Persistent rank columns for selected observations across model states.

    Unlike :class:`SelectedRankPanel`, this component does not replace the
    previous state's ranks. Each column remains visible, making sequential
    model comparisons readable without asking viewers to remember an earlier
    frame.
    """

    def __init__(
        self,
        scatter: EvolvingScatterPlot,
        labels: Mapping[str, str],
        *,
        states: Sequence[str] | None = None,
        state_headers: Mapping[str, str] | None = None,
        name_width: float = 2.0,
        name_font_size: float = 15,
        rank_font_size: float = 16,
        header_font_size: float = 13,
        row_spacing: float = 0.17,
        column_spacing: float = 0.32,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not labels:
            raise ValueError("a rank-history panel requires selected observations")
        unknown = set(labels) - set(scatter.dots_by_id)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(
                f"rank-history observations are absent from the scatter: {names}"
            )
        chosen_states = tuple(states or scatter.state_order)
        unknown_states = set(chosen_states) - set(scatter.state_order)
        if unknown_states:
            names = ", ".join(sorted(unknown_states))
            raise ValueError(f"rank-history states are absent from the scatter: {names}")

        name_labels = VGroup(
            *[
                fit_prose_text(
                    label,
                    max_width=name_width,
                    font_size=name_font_size,
                    min_font_size=11,
                    color=scatter.selected_colors[identifier],
                )
                for identifier, label in labels.items()
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=row_spacing)

        columns_by_state: dict[str, VGroup] = {}
        headers_by_state: dict[str, Text] = {}
        column_groups = VGroup()
        for state in chosen_states:
            ranks = scatter.ranks(state)
            column = VGroup(
                *[
                    Text(
                        f"#{ranks[identifier]}",
                        font_size=rank_font_size,
                        color=theme.foreground,
                    )
                    for identifier in labels
                ]
            ).arrange(DOWN, buff=row_spacing)
            header_text = (state_headers or {}).get(
                state,
                scatter.state_labels.get(state, state),
            )
            header = fit_prose_text(
                header_text,
                # Leave enough room for small cross-platform differences in
                # Pango's font metrics. The visual column width remains set by
                # the rendered header rather than by geometric scaling.
                max_width=max(1.00, column.width + 0.40),
                font_size=header_font_size,
                min_font_size=10,
                color=theme.muted,
                weight="BOLD",
            )
            column_group = VGroup(header, column).arrange(DOWN, buff=0.16)
            columns_by_state[state] = column
            headers_by_state[state] = header
            column_groups.add(column_group)

        column_groups.arrange(RIGHT, buff=column_spacing, aligned_edge=DOWN)
        body = VGroup(name_labels, column_groups).arrange(
            RIGHT,
            buff=column_spacing,
            aligned_edge=DOWN,
        )
        super().__init__(body)
        self.scatter = scatter
        self.identifiers = tuple(labels)
        self.states = chosen_states
        self.name_labels = name_labels
        self.columns_by_state = columns_by_state
        self.headers_by_state = headers_by_state
        self.state_groups = {
            state: VGroup(headers_by_state[state], columns_by_state[state])
            for state in chosen_states
        }


class NetworkInset(VGroup):
    """A dependency-free spatial network with values and linked highlights."""

    def __init__(
        self,
        links: Sequence[NetworkLink],
        *,
        width: float = 4.6,
        height: float = 2.8,
        selected_colors: Mapping[str, str] | None = None,
        values: Mapping[str, float] | None = None,
        value_range: tuple[float, float] | None = None,
        low_color: str | None = None,
        high_color: str | None = None,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not links:
            raise ValueError("a network inset requires at least one link")
        identifiers = [link.identifier for link in links]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("network-link identifiers must be unique")
        selected = dict(selected_colors or {})
        unknown = set(selected) - set(identifiers)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"selected links are absent from the network: {names}")
        encoded_values = dict(values or {})
        if encoded_values:
            missing = set(identifiers) - set(encoded_values)
            extra = set(encoded_values) - set(identifiers)
            if missing or extra:
                raise ValueError("network values must cover exactly the displayed links")
            if any(not math.isfinite(float(value)) for value in encoded_values.values()):
                raise ValueError("network values must be finite")
            lower, upper = value_range or (
                min(float(value) for value in encoded_values.values()),
                max(float(value) for value in encoded_values.values()),
            )
            if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
                raise ValueError("value_range must contain finite, increasing bounds")
        else:
            lower, upper = (0.0, 1.0)

        latitudes = [coordinate for link in links for coordinate in (link.start[1], link.end[1])]
        mean_latitude = sum(latitudes) / len(latitudes)
        longitude_scale = math.cos(math.radians(mean_latitude))
        projected = [
            (
                link.identifier,
                (link.start[0] * longitude_scale, link.start[1]),
                (link.end[0] * longitude_scale, link.end[1]),
            )
            for link in links
        ]
        xs = [coordinate for _, start, end in projected for coordinate in (start[0], end[0])]
        ys = [coordinate for _, start, end in projected for coordinate in (start[1], end[1])]
        x_mid = (min(xs) + max(xs)) / 2
        y_mid = (min(ys) + max(ys)) / 2
        x_span = max(max(xs) - min(xs), 1e-12)
        y_span = max(max(ys) - min(ys), 1e-12)
        scale = min(width / x_span, height / y_span)

        def point(coordinates: tuple[float, float]) -> np.ndarray:
            return np.array(
                [
                    (coordinates[0] - x_mid) * scale,
                    (coordinates[1] - y_mid) * scale,
                    0.0,
                ]
            )

        base_links = VGroup()
        base_by_id: dict[str, Line] = {}
        highlights: dict[str, Line] = {}
        for identifier, start, end in projected:
            if encoded_values:
                normalized = min(
                    1.0,
                    max(0.0, (float(encoded_values[identifier]) - lower) / (upper - lower)),
                )
                intensity = math.sqrt(normalized)
                color = interpolate_color(
                    ManimColor(low_color or theme.blue),
                    ManimColor(high_color or theme.orange),
                    normalized,
                )
                stroke_width = 0.9 + 2.8 * intensity
                opacity = 0.42 + 0.48 * intensity
            else:
                color = theme.grid
                stroke_width = 0.8
                opacity = 0.42
            line = Line(
                point(start),
                point(end),
                color=color,
                stroke_width=stroke_width,
            ).set_stroke(opacity=opacity)
            base_links.add(line)
            base_by_id[identifier] = line
            if identifier in selected:
                highlights[identifier] = Line(
                    point(start),
                    point(end),
                    color=selected[identifier],
                    stroke_width=5.2,
                )
        highlight_group = VGroup(*highlights.values())

        super().__init__(base_links, highlight_group)
        self.links = tuple(links)
        self.base_links = base_links
        self.base_by_id = base_by_id
        self.highlights = highlights
        self.highlight_group = highlight_group
        self.values = encoded_values
        self.value_range = (lower, upper) if encoded_values else None

    def isolate(self, identifier: str, *, dim_opacity: float = 0.18) -> VGroup:
        """Return a copy with one selected link emphasized."""

        if identifier not in self.highlights:
            raise KeyError(identifier)
        copy = self.copy()
        copy[0].set_stroke(opacity=dim_opacity)
        copy[1].set_opacity(0)
        highlight_ids = tuple(self.highlights)
        copy[1][highlight_ids.index(identifier)].set_stroke(width=8.5, opacity=1)
        return copy


class GeographicNetworkMap(VGroup):
    """A projected vector basemap with value-encoded and linkable network edges."""

    DEFAULT_COLORS = ("#46327E", "#365C8D", "#277F8E", "#4AC16D", "#FDE725")

    def __init__(
        self,
        regions: Sequence[GeographicRegion],
        links: Sequence[NetworkLink],
        *,
        values: Mapping[str, float],
        color_values: Mapping[str, float] | None = None,
        extent: tuple[float, float, float, float],
        value_range: tuple[float, float],
        color_range: tuple[float, float] | None = None,
        width: float = 10.2,
        height: float = 4.8,
        selected_colors: Mapping[str, str] | None = None,
        colors: Sequence[str] = DEFAULT_COLORS,
        legend_title: str = "Value",
        legend_ticks: Sequence[float] | None = None,
        show_legend: bool = True,
        show_graticule: bool = True,
        theme: VideoTheme = ECON_DARK,
    ) -> None:
        if not regions:
            raise ValueError("a geographic map requires at least one region")
        if len(colors) < 2:
            raise ValueError("a geographic map requires at least two scale colors")
        west, east, south, north = map(float, extent)
        if not west < east or not south < north:
            raise ValueError("extent must be ordered as west, east, south, north")
        lower, upper = map(float, value_range)
        if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
            raise ValueError("value_range must contain finite, increasing bounds")

        identifiers = [link.identifier for link in links]
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise ValueError("geographic network links must be nonempty and unique")
        encoded_values = dict(values)
        if set(encoded_values) != set(identifiers):
            raise ValueError("network values must cover exactly the displayed links")
        if any(not math.isfinite(float(value)) for value in encoded_values.values()):
            raise ValueError("network values must be finite")
        encoded_colors = dict(color_values or encoded_values)
        if set(encoded_colors) != set(identifiers):
            raise ValueError("network color values must cover exactly the displayed links")
        if any(not math.isfinite(float(value)) for value in encoded_colors.values()):
            raise ValueError("network color values must be finite")
        color_lower, color_upper = map(float, color_range or value_range)
        if (
            not math.isfinite(color_lower)
            or not math.isfinite(color_upper)
            or color_lower >= color_upper
        ):
            raise ValueError("color_range must contain finite, increasing bounds")
        selected = dict(selected_colors or {})
        if not set(selected).issubset(identifiers):
            raise ValueError("selected links must appear in the geographic network")

        mean_latitude = (south + north) / 2.0
        longitude_scale = math.cos(math.radians(mean_latitude))
        x_west, x_east = west * longitude_scale, east * longitude_scale
        x_mid = (x_west + x_east) / 2.0
        y_mid = (south + north) / 2.0
        scale = min(width / (x_east - x_west), height / (north - south))

        def point(coordinates: tuple[float, float]) -> np.ndarray:
            longitude, latitude = coordinates
            return np.array(
                [
                    (longitude * longitude_scale - x_mid) * scale,
                    (latitude - y_mid) * scale,
                    0.0,
                ]
            )

        graticule = VGroup()
        if show_graticule:
            longitude_start = math.ceil(west / 10.0) * 10
            latitude_start = math.ceil(south / 5.0) * 5
            for longitude in np.arange(longitude_start, east + 0.1, 10.0):
                graticule.add(
                    Line(
                        point((float(longitude), south)),
                        point((float(longitude), north)),
                        color=theme.grid,
                        stroke_width=0.65,
                    ).set_stroke(opacity=0.22)
                )
            for latitude in np.arange(latitude_start, north + 0.1, 5.0):
                graticule.add(
                    Line(
                        point((west, float(latitude))),
                        point((east, float(latitude))),
                        color=theme.grid,
                        stroke_width=0.65,
                    ).set_stroke(opacity=0.22)
                )

        land = VGroup()
        boundaries = VGroup()
        for region in regions:
            for ring in region.rings:
                projected = [point(coordinate) for coordinate in ring]
                shape = VMobject()
                shape.set_points_as_corners([*projected, projected[0]])
                shape.set_fill(theme.blue, opacity=0.035)
                shape.set_stroke(width=0)
                land.add(shape)
                outline = shape.copy().set_fill(opacity=0).set_stroke(
                    theme.muted,
                    width=0.75,
                    opacity=0.58,
                )
                boundaries.add(outline)

        road_underlays = VGroup()
        base_links = VGroup()
        underlay_by_id: dict[str, Line] = {}
        base_by_id: dict[str, Line] = {}
        highlights: dict[str, Line] = {}
        for link in links:
            start, end = point(link.start), point(link.end)
            normalized = min(
                1.0,
                max(0.0, (float(encoded_values[link.identifier]) - lower) / (upper - lower)),
            )
            color_normalized = min(
                1.0,
                max(
                    0.0,
                    (float(encoded_colors[link.identifier]) - color_lower)
                    / (color_upper - color_lower),
                ),
            )
            intensity = math.sqrt(normalized)
            stroke_width = 1.15 + 3.65 * intensity
            underlay = Line(
                start,
                end,
                color=theme.background,
                stroke_width=stroke_width + 2.2,
            ).set_stroke(opacity=0.74)
            road_underlays.add(underlay)
            underlay_by_id[link.identifier] = underlay
            line = Line(
                start,
                end,
                color=_sequential_color(color_normalized, colors),
                stroke_width=stroke_width,
            ).set_stroke(opacity=0.95)
            base_links.add(line)
            base_by_id[link.identifier] = line
            if link.identifier in selected:
                highlights[link.identifier] = Line(
                    start,
                    end,
                    color=selected[link.identifier],
                    stroke_width=6.0,
                ).set_stroke(opacity=0.0)
        highlight_group = VGroup(*highlights.values())

        # Keep an invisible local coordinate frame inside the map. Manim
        # applies every later shift, scale, or rotation to these points along
        # with the visible layers, allowing newly created markers to use the
        # map's current transform rather than its construction-time position.
        frame_step = 1.0e-4
        projection_frame = VGroup(
            VectorizedPoint(np.array([0.0, 0.0, 0.0])),
            VectorizedPoint(np.array([frame_step, 0.0, 0.0])),
            VectorizedPoint(np.array([0.0, frame_step, 0.0])),
        )

        legend = VGroup()
        if show_legend:
            steps = 32
            swatches = VGroup(
                *[
                    Rectangle(
                        width=0.24,
                        height=3.25 / steps + 0.01,
                        stroke_width=0,
                        fill_color=_sequential_color(step / (steps - 1), colors),
                        fill_opacity=1.0,
                    )
                    for step in range(steps)
                ]
            ).arrange(DOWN, buff=0)
            swatches.rotate(PI)
            ticks = tuple(legend_ticks or (lower, (lower + upper) / 2.0, upper))
            tick_labels = VGroup()
            for value in ticks:
                if value < lower or value > upper:
                    raise ValueError("legend ticks must lie within value_range")
                position = swatches.get_bottom() + UP * (
                    swatches.height * (float(value) - lower) / (upper - lower)
                )
                marker = Line(
                    position + LEFT * 0.04,
                    position + RIGHT * 0.12,
                    color=theme.foreground,
                    stroke_width=0.8,
                )
                label = Text(f"{value:g}", font_size=15, color=theme.foreground)
                label.next_to(marker, RIGHT, buff=0.07)
                tick_labels.add(VGroup(marker, label))
            title = Text(
                legend_title,
                font_size=16,
                color=theme.foreground,
                line_spacing=0.9,
            ).rotate(PI / 2)
            title.next_to(swatches, RIGHT, buff=0.62)
            legend.add(swatches, tick_labels, title)
            legend.next_to(VGroup(land, boundaries, base_links), RIGHT, buff=0.22)

        super().__init__(
            graticule,
            land,
            boundaries,
            road_underlays,
            base_links,
            highlight_group,
            legend,
            projection_frame,
        )
        self.regions = tuple(regions)
        self.links = tuple(links)
        self.road_underlays = road_underlays
        self.base_links = base_links
        self.road_lines = base_links
        self.underlay_by_id = underlay_by_id
        self.base_by_id = base_by_id
        self.highlights = highlights
        self.highlight_group = highlight_group
        self.legend = legend
        self.values = encoded_values
        self.value_range = (lower, upper)
        self.color_values = encoded_colors
        self.color_range = (color_lower, color_upper)
        self._independent_color_values = color_values is not None
        self._colors = tuple(colors)
        self._theme = theme
        self._project_local_point = point
        self._projection_frame = projection_frame
        self._projection_frame_step = frame_step

    def project_point(self, coordinates: tuple[float, float]) -> np.ndarray:
        """Project longitude and latitude into the map's local coordinates."""

        longitude, latitude = map(float, coordinates)
        if not math.isfinite(longitude) or not math.isfinite(latitude):
            raise ValueError("geographic coordinates must be finite")
        local = self._project_local_point((longitude, latitude))
        origin = self._projection_frame[0].get_center()
        x_basis = (
            self._projection_frame[1].get_center() - origin
        ) / self._projection_frame_step
        y_basis = (
            self._projection_frame[2].get_center() - origin
        ) / self._projection_frame_step
        return origin + local[0] * x_basis + local[1] * y_basis

    def location_markers(
        self,
        locations: Mapping[str, tuple[float, float]],
        *,
        color: str | None = None,
        radius: float = 0.038,
        fill_opacity: float = 0.94,
        stroke_width: float = 0.70,
        stroke_opacity: float = 0.92,
    ) -> VGroup:
        """Create stable, projected markers for a location-first map reveal.

        The returned group exposes ``marker_by_id`` so the same locations can
        be highlighted later without reconstructing them from coordinates.
        It is intentionally separate from the map: scenes can reveal, dim, or
        remove locations independently of the link network.
        """

        if not locations:
            raise ValueError("geographic locations cannot be empty")
        if radius <= 0 or not math.isfinite(radius):
            raise ValueError("location marker radius must be finite and positive")
        for name, value in {
            "fill_opacity": fill_opacity,
            "stroke_opacity": stroke_opacity,
        }.items():
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must lie between zero and one")
        if stroke_width < 0 or not math.isfinite(stroke_width):
            raise ValueError("location marker stroke width must be finite and nonnegative")

        marker_color = color or self._theme.green
        marker_by_id: dict[str, Dot] = {}
        for identifier, coordinates in locations.items():
            if not identifier:
                raise ValueError("geographic location identifiers cannot be empty")
            marker_by_id[identifier] = (
                Dot(
                    self.project_point(coordinates),
                    radius=radius,
                    color=marker_color,
                )
                .set_fill(opacity=fill_opacity)
                .set_stroke(
                    self._theme.background,
                    width=stroke_width,
                    opacity=stroke_opacity,
                )
            )
        markers = VGroup(*marker_by_id.values())
        markers.marker_by_id = marker_by_id
        return markers

    def network_skeleton(
        self,
        *,
        color: str | None = None,
        stroke_width: float = 0.90,
        opacity: float = 0.42,
    ) -> VGroup:
        """Return a neutral copy of every link for an extent-first reveal."""

        if stroke_width <= 0 or not math.isfinite(stroke_width):
            raise ValueError("network skeleton width must be finite and positive")
        if not math.isfinite(opacity) or not 0 <= opacity <= 1:
            raise ValueError("network skeleton opacity must lie between zero and one")
        skeleton_color = color or self._theme.muted
        skeleton_by_id = {
            identifier: line.copy().set_stroke(
                color=skeleton_color,
                width=stroke_width,
                opacity=opacity,
            )
            for identifier, line in self.base_by_id.items()
        }
        skeleton = VGroup(*skeleton_by_id.values())
        skeleton.skeleton_by_id = skeleton_by_id
        return skeleton

    def link_layers(self, identifiers: Sequence[str]) -> tuple[VGroup, VGroup]:
        """Return underlay and value-encoded line groups in the requested order."""

        requested = tuple(identifiers)
        if len(requested) != len(set(requested)):
            raise ValueError("requested geographic links must be unique")
        unknown = set(requested).difference(self.base_by_id)
        if unknown:
            raise ValueError(f"unknown geographic links: {sorted(unknown)}")
        return (
            VGroup(*(self.underlay_by_id[identifier] for identifier in requested)),
            VGroup(*(self.base_by_id[identifier] for identifier in requested)),
        )

    def animate_values(
        self,
        values: Mapping[str, float],
        *,
        color_values: Mapping[str, float] | None = None,
        run_time: float = 1.6,
    ) -> AnimationGroup:
        """Restyle the links while leaving the geographic frame fixed."""

        updated = dict(values)
        identifiers = tuple(link.identifier for link in self.links)
        if set(updated) != set(identifiers):
            raise ValueError("network values must cover exactly the displayed links")
        if any(not math.isfinite(float(value)) for value in updated.values()):
            raise ValueError("network values must be finite")
        updated_colors = (
            dict(color_values)
            if color_values is not None
            else (dict(self.color_values) if self._independent_color_values else updated)
        )
        if set(updated_colors) != set(identifiers):
            raise ValueError("network color values must cover exactly the displayed links")
        if any(not math.isfinite(float(value)) for value in updated_colors.values()):
            raise ValueError("network color values must be finite")
        lower, upper = self.value_range
        color_lower, color_upper = self.color_range
        target_underlays = self.road_underlays.copy()
        target_links = self.base_links.copy()
        for identifier, underlay, line in zip(
            identifiers,
            target_underlays,
            target_links,
            strict=True,
        ):
            normalized = min(
                1.0,
                max(0.0, (float(updated[identifier]) - lower) / (upper - lower)),
            )
            color_normalized = min(
                1.0,
                max(
                    0.0,
                    (float(updated_colors[identifier]) - color_lower)
                    / (color_upper - color_lower),
                ),
            )
            stroke_width = 1.15 + 3.65 * math.sqrt(normalized)
            underlay.set_stroke(
                color=self._theme.background,
                width=stroke_width + 2.2,
                opacity=0.74,
            )
            line.set_stroke(
                color=_sequential_color(color_normalized, self._colors),
                width=stroke_width,
                opacity=0.95,
            )
        self.values = updated
        self.color_values = updated_colors
        return AnimationGroup(
            Transform(self.road_underlays, target_underlays),
            Transform(self.base_links, target_links),
            lag_ratio=0,
            run_time=run_time,
        )

    def isolate(self, identifier: str, *, dim_opacity: float = 0.18) -> VGroup:
        """Return a copy with one selected geographic link emphasized."""

        if identifier not in self.highlights:
            raise KeyError(identifier)
        copy = self.copy()
        copy[3].set_stroke(opacity=min(0.30, dim_opacity))
        copy[4].set_stroke(opacity=dim_opacity)
        copy[5].set_opacity(0)
        highlight_ids = tuple(self.highlights)
        copy[5][highlight_ids.index(identifier)].set_stroke(width=8.5, opacity=1)
        return copy
