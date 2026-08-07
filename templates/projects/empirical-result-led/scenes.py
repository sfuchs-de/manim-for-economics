"""Paper-independent skeleton for an empirical-result-led explainer."""

from pathlib import Path

from manim import UP, Create, FadeIn, RoundedRectangle, VGroup

from econ_manim import (
    CausalChain,
    CoefficientPlot,
    ImpulseResponsePlot,
    ResearchScene,
    ShockDistribution,
    read_csv_rows,
)
from econ_manim import (
    ProseText as Text,
)

ROOT = Path(__file__).parent
VARIATION_ROWS = read_csv_rows(
    ROOT / "data" / "variation.csv",
    required_columns=("observation", "value"),
)
ESTIMATE_ROWS = read_csv_rows(
    ROOT / "data" / "estimates.csv",
    required_columns=("order", "label", "estimate", "lower", "upper", "color_role"),
)
RESPONSE_ROWS = read_csv_rows(
    ROOT / "data" / "response.csv",
    required_columns=("horizon", "estimate", "lower", "upper"),
)


def estimand_badge(theme):
    text = Text("effect of exposure on the outcome", font_size=23, color=theme.blue)
    box = RoundedRectangle(
        width=text.width + 0.52,
        height=0.70,
        corner_radius=0.13,
        stroke_color=theme.blue,
        stroke_width=1.7,
        fill_color=theme.card,
        fill_opacity=0.96,
    )
    text.move_to(box)
    return VGroup(box, text)


def coefficient_rows(theme, labels):
    selected = [row for row in ESTIMATE_ROWS if row["label"] in labels]
    return tuple(
        (
            row["label"],
            float(row["estimate"]),
            float(row["lower"]),
            float(row["upper"]),
            getattr(theme, row["color_role"]),
        )
        for row in selected
    )


class EmpiricalResultExplainer(ResearchScene):
    def construct(self):
        theme = self.theme
        self.next_section("question")
        self.show_title("Begin with one empirical question")
        self.set_caption("Replace the placeholders with the paper's estimand, sample, and unit.")
        question = Text(
            "How does exposure change the outcome?",
            font_size=34,
            color=theme.foreground,
        ).move_to([0, 0.35, 0])
        estimand = estimand_badge(theme).move_to([0, -0.85, 0])
        self.play(FadeIn(question, shift=UP * 0.08), run_time=0.65)
        self.play(FadeIn(estimand, shift=UP * 0.05), run_time=0.55)
        self.wait(1.6)
        self.clear_stage(question, run_time=0.35)

        self.next_section("variation")
        self.show_title("Show what identifies the response")
        self.set_caption(
            "Illustrative variation · state treatment, comparison, timing, and instrument."
        )
        self.play(estimand.animate.scale(0.82).move_to([0, 1.75, 0]), run_time=0.45)
        variation = ShockDistribution(
            tuple(
                (
                    float(row["value"]),
                    theme.orange if float(row["value"]) < 0 else theme.green,
                )
                for row in VARIATION_ROWS
            ),
            x_range=(-0.8, 0.8, 0.4),
            label="illustrative identifying variation",
            theme=theme,
        ).move_to([0, -0.40, 0])
        self.play(Create(variation.axis), FadeIn(variation[2]), run_time=0.55)
        self.play(FadeIn(variation.dots), run_time=0.65)
        self.wait(1.4)
        self.clear_stage(variation, run_time=0.35)

        self.next_section("estimate")
        self.show_title("Estimate that same response")
        self.set_caption(
            "Illustrative coefficient · report the estimand, units, confidence level, and sample."
        )
        central = CoefficientPlot(
            coefficient_rows(theme, {"overall estimate"}),
            x_label="effect of exposure on the outcome",
            theme=theme,
        ).scale(1.08).move_to([0, -0.45, 0])
        self.play(
            Create(central.axis),
            Create(central.reference),
            FadeIn(central.reference_label),
            run_time=0.60,
        )
        self.play(FadeIn(central.rows), FadeIn(central[0][-1]), run_time=0.70)
        self.wait(1.5)
        self.clear_stage(central, run_time=0.35)

        self.next_section("dynamics")
        self.show_title("Preserve the estimand across horizons")
        self.set_caption(
            "Illustrative path · include pre-periods and uncertainty when the design uses them."
        )
        horizons = tuple(float(row["horizon"]) for row in RESPONSE_ROWS)
        estimates = tuple(float(row["estimate"]) for row in RESPONSE_ROWS)
        lower = tuple(float(row["lower"]) for row in RESPONSE_ROWS)
        upper = tuple(float(row["upper"]) for row in RESPONSE_ROWS)
        response = ImpulseResponsePlot(
            {"response": (estimates, theme.blue)},
            horizons=horizons,
            confidence_intervals={"response": (lower, upper)},
            event_time=0,
            x_label="horizon relative to exposure",
            theme=theme,
        ).scale(1.02).move_to([0, -0.55, 0])
        self.play(
            Create(response.axes),
            Create(response.zero),
            Create(response.event),
            run_time=0.65,
        )
        self.play(FadeIn(response.bands), Create(response.lines), run_time=0.70)
        self.play(FadeIn(response.labels), FadeIn(response[-1]), run_time=0.45)
        self.wait(1.4)
        self.clear_stage(response, run_time=0.35)

        self.next_section("heterogeneity")
        self.show_title("Compare heterogeneity on one scale")
        self.set_caption(
            "Illustrative groups · motivate the split economically and preserve the reference."
        )
        groups = CoefficientPlot(
            coefficient_rows(theme, {"group A", "group B"}),
            x_label="same estimand · same units · same reference",
            theme=theme,
        ).scale(1.04).move_to([0, -0.45, 0])
        self.play(FadeIn(groups), run_time=0.75)
        self.wait(1.8)
        self.clear_stage(groups, estimand, run_time=0.40)

        self.next_section("interpretation")
        self.show_title("Stop at the identification frontier")
        self.set_caption(
            "State the supported interpretation, then name what the design does not establish."
        )
        conclusion = CausalChain(
            (
                ("identifying variation", theme.orange),
                ("estimated response", theme.blue),
                ("economic magnitude", theme.green),
                ("supported claim", theme.foreground),
            ),
            theme=theme,
        ).move_to([0, 0.15, 0])
        self.play(FadeIn(conclusion), run_time=0.75)
        self.wait(2.0)
