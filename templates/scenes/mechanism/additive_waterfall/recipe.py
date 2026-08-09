"""Atomic recipe for an additive benchmark-to-result decomposition."""

from pathlib import Path

from manim import Create, FadeIn

from econ_manim import AdditiveWaterfallChart, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "waterfall.csv",
    required_columns=("order", "kind", "label", "value", "color_role"),
)


def make_additive_waterfall(theme):
    ordered = sorted(ROWS, key=lambda row: int(row["order"]))
    baseline_rows = [row for row in ordered if row["kind"] == "baseline"]
    change_rows = [row for row in ordered if row["kind"] == "change"]
    total_rows = [row for row in ordered if row["kind"] == "total"]
    if len(baseline_rows) != 1 or len(total_rows) != 1 or not change_rows:
        raise ValueError("waterfall data require one baseline, changes, and one total")
    baseline = baseline_rows[0]
    total = total_rows[0]
    return AdditiveWaterfallChart(
        (
            baseline["label"],
            float(baseline["value"]),
            getattr(theme, baseline["color_role"]),
        ),
        tuple(
            (
                row["label"],
                float(row["value"]),
                getattr(theme, row["color_role"]),
            )
            for row in change_rows
        ),
        total_label=total["label"],
        total_color=getattr(theme, total["color_role"]),
        display_unit="bp",
        speech_unit="basis points",
        footer="Illustrative values · exact inputs, rounded labels",
        theme=theme,
    )


def build_additive_waterfall(scene):
    chart = make_additive_waterfall(scene.theme)
    scene.play(
        Create(chart.zero),
        FadeIn(chart.bars[0]),
        FadeIn(chart.labels[0]),
        FadeIn(chart.amounts[0]),
        run_time=0.55,
    )
    for index in range(1, len(chart.bars)):
        scene.play(
            Create(chart.connectors[index - 1]),
            FadeIn(chart.bars[index]),
            FadeIn(chart.labels[index]),
            FadeIn(chart.amounts[index]),
            run_time=0.65,
        )
    if chart.footer is not None:
        scene.play(FadeIn(chart.footer), run_time=0.30)
    scene.wait(0.80)
    return chart


class AdditiveWaterfallRecipe(ResearchScene):
    def construct(self):
        self.show_title(
            "Show what each mechanism adds or subtracts",
            run_time=0.45,
        )
        build_additive_waterfall(self)
