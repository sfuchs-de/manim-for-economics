"""Atomic recipe for following observations through model specifications."""

from pathlib import Path

from manim import Create, FadeIn, VGroup

from econ_manim import (
    EvolvingScatterPlot,
    ResearchScene,
    ScatterObservation,
    SelectedRankPanel,
    ranked_value_groups,
    read_csv_rows,
)

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "observations.csv",
    required_columns=(
        "id",
        "label",
        "benchmark",
        "direct",
        "adjustment",
        "final",
        "color_role",
    ),
)


def build_evolving_scatter(scene):
    theme = scene.theme
    observations = tuple(
        ScatterObservation(
            row["id"],
            float(row["benchmark"]),
            {
                "direct": float(row["direct"]),
                "adjustment": float(row["adjustment"]),
                "final": float(row["final"]),
            },
            row["label"],
        )
        for row in ROWS
    )
    selected = {
        row["id"]: getattr(theme, row["color_role"])
        for row in ROWS
        if row["color_role"]
    }
    scatter = EvolvingScatterPlot(
        observations,
        ("direct", "adjustment", "final"),
        state_labels={
            "direct": "benchmark",
            "adjustment": "after equilibrium adjustment",
            "final": "reported welfare measure",
        },
        selected_colors=selected,
        x_range=(0, 1, 0.25),
        y_range=(0, 1, 0.25),
        x_label="benchmark measure",
        y_label="model-based measure",
        theme=theme,
    ).scale(0.84).move_to([-1.60, -0.35, 0])
    selected_labels = {
        row["id"]: row["label"]
        for row in ROWS
        if row["color_role"]
    }
    ranks = SelectedRankPanel(scatter, selected_labels, theme=theme)
    ranks.scale(0.94).move_to([4.15, -0.20, 0])

    scene.play(
        Create(scatter.axes),
        Create(scatter.diagonal),
        FadeIn(scatter[3:]),
        run_time=0.65,
    )
    benchmark_values = {
        observation.identifier: observation.benchmark
        for observation in observations
    }
    for identifiers in ranked_value_groups(benchmark_values, groups=3):
        scene.play(FadeIn(scatter.dot_layers(identifiers)), run_time=0.40)
        scene.wait(0.12)
    scene.play(FadeIn(ranks), run_time=0.45)
    scene.wait(0.7)
    for state in ("adjustment", "final"):
        trails = scatter.transition_lines(state)
        scene.play(
            Create(trails),
            scatter.state_label.animate.set_opacity(0),
            ranks.state_label.animate.set_opacity(0),
            ranks.rank_labels.animate.set_opacity(0),
            run_time=0.35,
        )
        scene.play(scatter.animate_to(state), ranks.animate_to(state), run_time=1.6)
        scene.play(
            scatter.state_label.animate.set_opacity(1),
            ranks.state_label.animate.set_opacity(1),
            ranks.rank_labels.animate.set_opacity(1),
            run_time=0.25,
        )
        scene.wait(0.7)
    scene.wait(0.8)
    return VGroup(scatter, ranks)


class EvolvingScatterRecipe(ResearchScene):
    def construct(self):
        self.show_title("Follow the same observations across model states", run_time=0.45)
        self.set_caption(
            "Illustrative values · keep the benchmark fixed and recompute ranks from each state.",
            run_time=0.35,
        )
        build_evolving_scatter(self)
