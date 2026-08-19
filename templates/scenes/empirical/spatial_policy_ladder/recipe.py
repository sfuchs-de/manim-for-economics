"""Composite map-scatter-rank recipe for an ordered policy-model ladder."""

from pathlib import Path

from manim import DOWN, FadeIn, VGroup

from econ_manim import (
    LinkedEmpiricalViews,
    NetworkLink,
    ResearchScene,
    ScatterObservation,
    SpatialStateDataset,
    read_csv_rows,
    read_geojson_regions,
)

DATA_DIR = Path(__file__).with_name("data")
ROWS = read_csv_rows(
    DATA_DIR / "network_states.csv",
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
REGIONS = read_geojson_regions(DATA_DIR / "regions.geojson", identifier_property="id")


def _dataset():
    observations = tuple(
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
    )
    links = tuple(
        NetworkLink(
            row["id"],
            (float(row["x1"]), float(row["y1"])),
            (float(row["x2"]), float(row["y2"])),
        )
        for row in ROWS
    )
    selected = {row["id"]: row["label"] for row in ROWS if row["color_role"]}
    return SpatialStateDataset(
        observations,
        links,
        ("traditional", "spatial", "extended"),
        "index points",
        state_labels={
            "traditional": "Traditional",
            "spatial": "Spatial adjustment",
            "extended": "Extended",
        },
        selected_labels=selected,
    )


def build_spatial_policy_ladder(scene):
    dataset = _dataset()
    selected_colors = {
        row["id"]: getattr(scene.theme, row["color_role"])
        for row in ROWS
        if row["color_role"]
    }
    views = LinkedEmpiricalViews(
        dataset,
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
        theme=scene.theme,
    )
    views.scatter.move_to([-3.35, 0.10, 0])
    views.map.move_to([3.65, 0.58, 0])
    views.rank_history.next_to(views.map, DOWN, buff=0.18)
    stage = VGroup(views.scatter, views.map, views.rank_history)
    scene.validate_stage(stage, name="spatial policy ladder")

    scene.play(FadeIn(views.scatter), FadeIn(views.map), FadeIn(views.rank_history), run_time=0.8)
    scene.wait(0.55)
    scene.play(views.animate_to("spatial", run_time=1.45))
    scene.wait(0.60)
    scene.play(views.animate_to("extended", run_time=1.45))
    scene.wait(1.0)
    return stage


class SpatialPolicyLadderRecipe(ResearchScene):
    def construct(self):
        self.show_title("Track one network through an ordered policy-model ladder", run_time=0.45)
        self.set_caption(
            "Illustrative values; map, scatter, and ranks share one validated data contract",
            run_time=0.30,
        )
        build_spatial_policy_ladder(self)
