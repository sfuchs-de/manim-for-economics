"""Composite recipe following one observation across linked empirical views."""

from pathlib import Path

from manim import FadeIn, FadeOut, VGroup

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
    ),
)
REGIONS = read_geojson_regions(DATA_DIR / "regions.geojson", identifier_property="id")
SELECTED_ID = "center_east"


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
        selected_labels={SELECTED_ID: "Center to East"},
    )


def build_selected_observation_biography(scene):
    dataset = _dataset()
    views = LinkedEmpiricalViews(
        dataset,
        REGIONS,
        extent=(-1.0, 11.0, -1.0, 7.0),
        selected_colors={SELECTED_ID: scene.theme.orange},
        scatter_width=5.8,
        scatter_height=3.35,
        map_width=5.3,
        map_height=3.0,
        rank_headers={
            "traditional": "Trad.",
            "spatial": "Spatial",
            "extended": "Extended",
        },
        track_rank_history=False,
        theme=scene.theme,
    )
    views.scatter.move_to([-3.3, 0.15, 0])
    views.map.move_to([3.55, 0.55, 0])
    views.map.base_links.set_stroke(opacity=0.22)
    views.map.highlights[SELECTED_ID].set_stroke(opacity=1.0)
    trajectory = VGroup()
    stage = VGroup(views.scatter, views.map)
    scene.validate_stage(stage, name="selected observation biography")

    scene.play(FadeIn(stage), run_time=0.75)
    scene.wait(0.45)
    for state in ("spatial", "extended"):
        next_line = views.scatter.transition_lines(state, identifiers=(SELECTED_ID,))
        scene.play(FadeIn(next_line), views.animate_to(state, run_time=1.25))
        trajectory.add(next_line)
        scene.wait(0.45)

    card = SelectedObservationCard(
        dataset,
        SELECTED_ID,
        color=scene.theme.orange,
        theme=scene.theme,
    ).move_to([3.55, -0.25, 0])
    scene.play(FadeOut(views.map), FadeIn(card), run_time=0.65)
    scene.wait(1.1)
    return VGroup(views.scatter, trajectory, card)


class SelectedObservationBiographyRecipe(ResearchScene):
    def construct(self):
        self.show_title("Explain a ranking change through one observation", run_time=0.45)
        self.set_caption(
            "Illustrative values; the selected link keeps one identifier across every view",
            run_time=0.30,
        )
        build_selected_observation_biography(self)
