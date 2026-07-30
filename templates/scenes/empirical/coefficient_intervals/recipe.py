"""Atomic recipe for directly labeled estimates and confidence intervals."""

from pathlib import Path

from manim import Create, FadeIn

from econ_manim import CoefficientPlot, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "coefficients.csv",
    required_columns=(
        "order",
        "label",
        "estimate",
        "lower",
        "upper",
        "color_role",
    ),
)


def make_coefficient_plot(theme):
    ordered = sorted(ROWS, key=lambda row: int(row["order"]))
    return CoefficientPlot(
        tuple(
            (
                row["label"],
                float(row["estimate"]),
                float(row["lower"]),
                float(row["upper"]),
                getattr(theme, row["color_role"]),
            )
            for row in ordered
        ),
        x_label="illustrative effect · common scale",
        theme=theme,
    )


def build_coefficient_intervals(scene):
    plot = make_coefficient_plot(scene.theme)
    scene.play(
        Create(plot.axis),
        Create(plot.reference),
        FadeIn(plot.reference_label),
        run_time=0.55,
    )
    for row in plot.rows:
        scene.play(FadeIn(row), run_time=0.55)
    scene.play(FadeIn(plot[0][-1]), run_time=0.35)
    scene.wait(0.9)
    return plot


class CoefficientIntervalsRecipe(ResearchScene):
    def construct(self):
        self.show_title("Compare estimates on one honest scale", run_time=0.45)
        self.set_caption(
            "Illustrative values · state the estimand, confidence level, and reference.",
            run_time=0.35,
        )
        build_coefficient_intervals(self)
