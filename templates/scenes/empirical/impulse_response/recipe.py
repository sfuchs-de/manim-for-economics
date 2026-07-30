"""Atomic recipe for a dynamic response with uncertainty."""

from pathlib import Path

from manim import Create, FadeIn

from econ_manim import ImpulseResponsePlot, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "impulse_response.csv",
    required_columns=("horizon", "estimate", "lower", "upper"),
)


def make_impulse_response(theme):
    horizons = tuple(float(row["horizon"]) for row in ROWS)
    estimates = tuple(float(row["estimate"]) for row in ROWS)
    lower = tuple(float(row["lower"]) for row in ROWS)
    upper = tuple(float(row["upper"]) for row in ROWS)
    return ImpulseResponsePlot(
        {"response": (estimates, theme.blue)},
        horizons=horizons,
        confidence_intervals={"response": (lower, upper)},
        event_time=0,
        x_label="horizon relative to event",
        theme=theme,
    )


def build_impulse_response(scene):
    plot = make_impulse_response(scene.theme)
    scene.play(
        Create(plot.axes),
        Create(plot.zero),
        Create(plot.event),
        run_time=0.65,
    )
    scene.play(FadeIn(plot.bands), run_time=0.45)
    scene.play(Create(plot.lines), FadeIn(plot.labels), run_time=0.75)
    scene.play(FadeIn(plot[-1]), run_time=0.30)
    scene.wait(0.9)
    return plot


class ImpulseResponseRecipe(ResearchScene):
    def construct(self):
        self.show_title("Show dynamics and uncertainty together", run_time=0.45)
        self.set_caption(
            "Illustrative values · state the estimand, horizon, units, and confidence level.",
            run_time=0.35,
        )
        build_impulse_response(self)
