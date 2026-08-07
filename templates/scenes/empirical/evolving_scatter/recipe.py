"""Atomic recipe for following observations through model specifications."""

from pathlib import Path

from manim import Create, FadeIn, VGroup

from econ_manim import (
    EvolvingScatterPlot,
    ResearchScene,
    ScatterObservation,
    SelectedRankHistoryPanel,
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
        width=6.05,
        height=4.03,
        x_label="benchmark measure",
        y_label="model-based measure",
        theme=theme,
    ).move_to([-1.60, -0.35, 0])
    selected_labels = {
        row["id"]: row["label"]
        for row in ROWS
        if row["color_role"]
    }
    ranks = SelectedRankHistoryPanel(
        scatter,
        selected_labels,
        state_headers={
            "direct": "Benchmark",
            "adjustment": "Adjustment",
            "final": "Final",
        },
        name_width=1.55,
        name_font_size=13,
        rank_font_size=14,
        header_font_size=11,
        row_spacing=0.14,
        column_spacing=0.22,
        theme=theme,
    ).move_to([4.15, -0.20, 0])
    for state in ("adjustment", "final"):
        ranks.state_groups[state].set_opacity(0)

    scene.validate_stage(scatter, ranks, name="evolving scatter")
    scene.add(ranks.state_groups["adjustment"], ranks.state_groups["final"])

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
    scene.play(
        FadeIn(ranks.name_labels),
        FadeIn(ranks.state_groups["direct"]),
        run_time=0.45,
    )
    scene.wait(0.7)
    for state in ("adjustment", "final"):
        trails = scatter.transition_lines(state)
        scene.play(
            Create(trails),
            scatter.state_label.animate.set_opacity(0),
            run_time=0.35,
        )
        scene.play(scatter.animate_to(state), run_time=1.6)
        scene.play(
            scatter.state_label.animate.set_opacity(1),
            ranks.state_groups[state].animate.set_opacity(1),
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
