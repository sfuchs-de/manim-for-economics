"""Complete synthetic example of a linked spatial policy comparison."""

from pathlib import Path

from manim import DOWN, Create, FadeIn, FadeOut, LaggedStart, VGroup

from econ_manim import (
    LinkedEmpiricalViews,
    NetworkLink,
    ResearchScene,
    ScatterObservation,
    SelectedObservationCard,
    SpatialStateDataset,
    read_csv_rows,
    read_geojson_regions,
)

ROOT = Path(__file__).resolve().parent
ROWS = read_csv_rows(
    ROOT / "data" / "network_states.csv",
    required_columns=(
        "id",
        "label",
        "x1",
        "y1",
        "x2",
        "y2",
        "benchmark",
        "spatial",
        "extended",
        "color_role",
    ),
)
REGIONS = read_geojson_regions(ROOT / "data" / "regions.geojson", identifier_property="id")


def dataset():
    return SpatialStateDataset(
        tuple(
            ScatterObservation(
                row["id"],
                float(row["benchmark"]),
                {
                    "traditional": float(row["benchmark"]),
                    "spatial": float(row["spatial"]),
                    "extended": float(row["extended"]),
                },
                row["label"],
            )
            for row in ROWS
        ),
        tuple(
            NetworkLink(
                row["id"],
                (float(row["x1"]), float(row["y1"])),
                (float(row["x2"]), float(row["y2"])),
            )
            for row in ROWS
        ),
        ("traditional", "spatial", "extended"),
        "index points",
        state_labels={
            "traditional": "Traditional",
            "spatial": "Spatial adjustment",
            "extended": "Extended",
        },
        selected_labels={
            row["id"]: row["label"] for row in ROWS if row["color_role"]
        },
    )


class NetworkPolicyLadderExample(ResearchScene):
    def construct(self):
        data = dataset()
        selected_colors = {
            row["id"]: getattr(self.theme, row["color_role"])
            for row in ROWS
            if row["color_role"]
        }
        views = LinkedEmpiricalViews(
            data,
            REGIONS,
            extent=(-1.0, 11.0, -1.0, 7.0),
            selected_colors=selected_colors,
            scatter_width=5.8,
            scatter_height=3.35,
            map_width=5.3,
            map_height=3.0,
            rank_headers={
                "traditional": "Trad.",
                "spatial": "Spatial",
                "extended": "Extended",
            },
            theme=self.theme,
        )

        self.show_title("Build one linked network-policy comparison", run_time=0.45)
        self.set_caption(
            "Illustrative synthetic network; values share one sample, identifier, and unit",
            run_time=0.30,
        )
        views.map.move_to([0, 0.15, 0])
        locations = {
            f"{x:g},{y:g}": (x, y)
            for link in data.links
            for x, y in (link.start, link.end)
        }
        markers = views.map.location_markers(locations, color=self.theme.green)
        skeleton = views.map.network_skeleton()
        visible_map = VGroup(views.map[1], views.map[2], markers, skeleton)
        self.validate_stage(visible_map, name="network input reveal")
        self.play(FadeIn(views.map[1]), Create(views.map[2]), FadeIn(markers), run_time=0.65)
        self.play(
            markers.animate.set_opacity(0.35),
            LaggedStart(*[Create(line) for line in skeleton], lag_ratio=0.04),
            run_time=0.75,
        )
        self.play(
            skeleton.animate.set_stroke(opacity=0.15),
            FadeIn(views.map.road_underlays),
            FadeIn(views.map.base_links),
            run_time=0.65,
        )
        self.wait(0.45)

        self.play(FadeOut(markers), FadeOut(skeleton), run_time=0.35)
        views.map.move_to([3.65, 0.58, 0])
        views.scatter.move_to([-3.35, 0.10, 0])
        views.rank_history.next_to(views.map, DOWN, buff=0.18)
        comparison = VGroup(views.scatter, views.map, views.rank_history)
        self.validate_stage(comparison, name="linked comparison")
        self.play(FadeIn(views.scatter), FadeIn(views.rank_history), run_time=0.70)
        self.play(views.animate_to("spatial", run_time=1.35))
        self.wait(0.45)
        self.play(views.animate_to("extended", run_time=1.35))
        self.wait(0.55)

        selected_id = "center_east"
        card = SelectedObservationCard(
            data,
            selected_id,
            color=selected_colors[selected_id],
            theme=self.theme,
        ).move_to([3.65, -0.25, 0])
        self.play(
            views.map.base_links.animate.set_stroke(opacity=0.18),
            views.map.highlights[selected_id].animate.set_stroke(
                width=8.5,
                opacity=1.0,
            ),
            run_time=0.40,
        )
        self.play(
            FadeOut(views.map),
            FadeOut(views.rank_history),
            FadeIn(card),
            run_time=0.65,
        )
        self.wait(1.1)
