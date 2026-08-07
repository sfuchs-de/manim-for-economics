"""Atomic recipe for a value-encoded geographic network map.

The bundled demonstration uses the paper's public-safe U.S. highway artifacts.
"""

from pathlib import Path

from manim import DOWN, LEFT, RIGHT, Create, FadeIn, FadeOut, LaggedStart, Rectangle, VGroup

from econ_manim import (
    GeographicNetworkMap,
    NetworkLink,
    ResearchScene,
    ranked_value_groups,
    read_csv_rows,
    read_geojson_regions,
)
from econ_manim import (
    ProseText as Text,
)

DATA_DIR = Path(__file__).with_name("data")
ROWS = read_csv_rows(
    DATA_DIR / "network_links.csv",
    required_columns=(
        "physical_link_id",
        "longitude_a",
        "latitude_a",
        "longitude_b",
        "latitude_b",
        "hulten",
    ),
)
REGIONS = read_geojson_regions(
    DATA_DIR / "regions.geojson",
    identifier_property="STUSPS",
)

CONUS_EXTENT = (-125.0, -66.0, 24.0, 50.0)
TRAFFIC_COLORS = ("#321052", "#414487", "#257B8E", "#3BAA72", "#D5B400")
SELECTED_LABELS = {
    "6_10": "Los Angeles–San Diego",
    "184_200": "Washington–Baltimore",
    "96_97": "Chicago–Milwaukee",
}


def _status(text, *, color, font_size=22):
    return Text(text, font_size=font_size, color=color).move_to([0, 2.62, 0])


def _traffic_values():
    """Return bidirectional traffic shares in basis points of domestic income."""

    return {
        row["physical_link_id"]: 1.0e4 * float(row["hulten"])
        for row in ROWS
    }


def _network_locations():
    """Return unique endpoints with deterministic identifiers."""

    locations = {}
    for row in ROWS:
        for suffix in ("a", "b"):
            coordinates = (
                float(row[f"longitude_{suffix}"]),
                float(row[f"latitude_{suffix}"]),
            )
            identifier = f"{coordinates[0]:.6f},{coordinates[1]:.6f}"
            locations.setdefault(identifier, coordinates)
    return locations


def _traffic_legend(*, theme, low, high):
    swatches = VGroup(
        *[
            Rectangle(
                width=0.26,
                height=0.25,
                stroke_width=0,
                fill_color=color,
                fill_opacity=1.0,
            )
            for color in reversed(TRAFFIC_COLORS)
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.015)
    heading = Text("Traffic share", font_size=15, color=theme.foreground).next_to(
        swatches, LEFT, buff=0.14
    )
    heading.rotate(1.5708)
    high_label = Text(
        f"{high:.1f} bp · high", font_size=12, color=theme.foreground
    ).next_to(swatches[0], RIGHT, buff=0.08)
    low_label = Text(
        f"{low:.2f} bp · low", font_size=12, color=theme.foreground
    ).next_to(swatches[-1], RIGHT, buff=0.08)
    return VGroup(heading, swatches, high_label, low_label)


def build_geographic_network_map(scene):
    theme = scene.theme
    links = tuple(
        NetworkLink(
            row["physical_link_id"],
            (float(row["longitude_a"]), float(row["latitude_a"])),
            (float(row["longitude_b"]), float(row["latitude_b"])),
        )
        for row in ROWS
    )
    values = _traffic_values()
    selected = {
        "6_10": theme.orange,
        "184_200": theme.green,
        "96_97": theme.blue,
    }

    network = GeographicNetworkMap(
        REGIONS,
        links,
        values=values,
        extent=CONUS_EXTENT,
        value_range=(0.0, 20.0),
        width=10.0,
        height=4.65,
        selected_colors=selected,
        show_legend=False,
        show_graticule=False,
        theme=theme,
    )

    groups = ranked_value_groups(values, groups=5, descending=False)
    for color, identifiers in zip(TRAFFIC_COLORS, groups, strict=True):
        for identifier in identifiers:
            network.base_by_id[identifier].set_stroke(color=color)
    legend = _traffic_legend(
        theme=theme,
        low=min(values.values()),
        high=max(values.values()),
    ).next_to(VGroup(network[1], network[2], network.base_links), RIGHT, buff=0.22)

    locations = network.location_markers(
        _network_locations(),
        color=theme.green,
        radius=0.032,
    )
    network.add(locations)
    # Project locations before translating the complete map so every
    # geographic layer receives the same transform.
    network.move_to([0, -0.10, 0])
    skeleton = network.network_skeleton(
        color=theme.muted,
        stroke_width=0.90,
        opacity=0.42,
    )
    scene.validate_stage(network, skeleton, name="geographic network")

    scene.play(FadeIn(network[1]), Create(network[2]), run_time=0.65)
    status = _status("Begin with the network's economic locations", color=theme.green)
    scene.play(
        FadeIn(status),
        LaggedStart(*[FadeIn(marker) for marker in locations], lag_ratio=0.01),
        run_time=0.85,
    )
    scene.wait(0.45)

    next_status = _status(
        "Show the full network before encoding traffic",
        color=theme.foreground,
    )
    scene.play(
        FadeOut(status),
        FadeIn(next_status),
        locations.animate.set_opacity(0.42),
        LaggedStart(*[Create(line) for line in skeleton], lag_ratio=0.006),
        run_time=0.90,
    )
    status = next_status
    scene.wait(0.50)

    next_status = _status(
        "Overlay link values from low to high traffic",
        color=theme.foreground,
    )
    scene.play(
        FadeOut(status),
        FadeIn(next_status),
        locations.animate.set_opacity(0.16),
        skeleton.animate.set_stroke(opacity=0.20),
        FadeIn(legend),
        run_time=0.45,
    )
    status = next_status

    for index, identifiers in enumerate(groups, start=1):
        underlays, lines = network.link_layers(identifiers)
        if index == 1:
            status_text = "Lowest-traffic quintile"
        elif index == len(groups):
            status_text = "Highest-traffic quintile"
        else:
            status_text = f"Traffic quintile {index} of {len(groups)}"
        next_status = _status(status_text, color=theme.foreground)
        scene.play(FadeOut(status), run_time=0.12)
        scene.remove(status)
        status = next_status
        scene.play(
            FadeIn(status),
            FadeIn(underlays),
            LaggedStart(*[Create(line) for line in lines], lag_ratio=0.10),
            run_time=0.50,
        )
        scene.wait(0.15)

    scene.play(FadeOut(status), run_time=0.18)
    network.road_underlays.set_stroke(opacity=0.28)
    network.base_links.set_stroke(opacity=0.26)
    selected_ids = tuple(selected)
    for identifier in selected_ids:
        highlight = network.highlights[identifier]
        label = _status(SELECTED_LABELS[identifier], color=theme.foreground, font_size=23)
        scene.play(FadeIn(label), highlight.animate.set_stroke(opacity=1.0), run_time=0.48)
        scene.wait(0.72)
        if identifier != selected_ids[-1]:
            scene.play(FadeOut(label), highlight.animate.set_stroke(opacity=0.42), run_time=0.28)
        else:
            scene.wait(0.45)
    return VGroup(network, locations, skeleton, legend, label)


class GeographicNetworkMapRecipe(ResearchScene):
    def construct(self):
        self.show_title("Build a U.S. network map from verified link-level data", run_time=0.45)
        self.set_caption(
            "HPMS 2012 traffic counts · 2018 Census TIGER/Line · derived paper artifacts",
            run_time=0.35,
        )
        build_geographic_network_map(self)
