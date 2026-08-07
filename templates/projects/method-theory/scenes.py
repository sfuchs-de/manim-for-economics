"""Paper-independent skeleton for a method- or theory-led explainer."""

from pathlib import Path

from manim import RIGHT, UP, Create, FadeIn, RoundedRectangle, VGroup

from econ_manim import (
    CausalChain,
    ChannelDecomposition,
    DivergingBarChart,
    EquationBuild,
    LinkedViews,
    ResearchScene,
    read_csv_rows,
)
from econ_manim import (
    ProseText as Text,
)

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "comparative_statics.csv",
    required_columns=("order", "label", "value", "color_role"),
)


def object_badge(theme, text="economic object"):
    label = Text(text, font_size=23, color=theme.blue)
    box = RoundedRectangle(
        width=label.width + 0.52,
        height=0.70,
        corner_radius=0.13,
        stroke_color=theme.blue,
        stroke_width=1.7,
        fill_color=theme.card,
        fill_opacity=0.96,
    )
    label.move_to(box)
    return VGroup(box, label)


class MethodTheoryExplainer(ResearchScene):
    def construct(self):
        theme = self.theme
        self.next_section("problem")
        self.show_title("Begin with the problem the method solves")
        self.set_caption("Name what is hard to identify, compute, measure, or interpret.")
        problem = Text(
            "The target is not directly available.",
            font_size=34,
            color=theme.foreground,
        ).move_to([0, 0.40, 0])
        persistent = object_badge(theme).move_to([0, -0.85, 0])
        self.play(FadeIn(problem, shift=UP * 0.08), run_time=0.65)
        self.play(FadeIn(persistent), run_time=0.50)
        self.wait(1.7)
        self.clear_stage(problem, run_time=0.35)

        self.next_section("object")
        self.show_title("Define only the object the viewer needs")
        self.set_caption("Use words first; introduce notation only after every symbol has meaning.")
        self.play(persistent.animate.scale(0.82).move_to([0, 1.75, 0]), run_time=0.45)
        definition = EquationBuild(
            (
                ("state", theme.blue),
                ("choice", theme.green),
                ("constraint", theme.orange),
            ),
            lhs="economic object",
            operators=("+", "+"),
            theme=theme,
        ).move_to([0, -0.30, 0])
        self.play(FadeIn(VGroup(definition.lhs, definition.equals)), run_time=0.45)
        for index, term in enumerate(definition.terms):
            animations = [FadeIn(term)]
            if index:
                animations.insert(0, FadeIn(definition.operators[index - 1]))
            self.play(*animations, run_time=0.45)
        self.wait(1.3)
        self.clear_stage(definition, run_time=0.35)

        self.next_section("operation")
        self.show_title("Apply one transparent operation")
        self.set_caption(
            "The transformation should carry the economic argument, not decorative motion."
        )
        operation = CausalChain(
            (
                ("economic object", theme.blue),
                ("condition", theme.orange),
                ("operation", theme.green),
                ("target", theme.foreground),
            ),
            theme=theme,
        ).move_to([0, -0.25, 0])
        self.play(FadeIn(operation.nodes[0]), run_time=0.40)
        for arrow, node in zip(operation.arrows, operation.nodes[1:], strict=True):
            self.play(Create(arrow), FadeIn(node, shift=RIGHT * 0.06), run_time=0.50)
        self.wait(1.4)
        self.clear_stage(operation, run_time=0.35)

        self.next_section("result")
        self.show_title("State the result in economic language")
        self.set_caption("Reveal formal notation only when it adds precision beyond the words.")
        result = EquationBuild(
            (
                ("direct term", theme.blue),
                ("adjustment term", theme.green),
            ),
            lhs="identified target",
            operators=("+",),
            theme=theme,
        ).move_to([0, -0.25, 0])
        self.play(FadeIn(VGroup(result.lhs, result.equals)), run_time=0.45)
        self.play(FadeIn(result.terms[0]), run_time=0.45)
        self.play(
            FadeIn(result.operators[0]),
            FadeIn(result.terms[1]),
            run_time=0.55,
        )
        self.wait(1.6)
        self.clear_stage(result, run_time=0.35)

        self.next_section("comparative-static")
        self.show_title("Change one condition and hold the benchmark fixed")
        self.set_caption("Illustrative values · replace with a proved or documented comparison.")
        comparison = DivergingBarChart(
            tuple(
                (
                    row["label"],
                    float(row["value"]),
                    getattr(theme, row["color_role"]),
                )
                for row in sorted(ROWS, key=lambda row: int(row["order"]))
            ),
            benchmark_label="benchmark",
            left_label="smaller target",
            right_label="larger target",
            value_format="{:+.0f}",
            theme=theme,
        ).move_to([0, -0.30, 0])
        self.play(FadeIn(comparison), run_time=0.75)
        self.wait(1.8)
        self.clear_stage(comparison, run_time=0.35)

        self.next_section("application")
        self.show_title("Connect the abstract result to its use")
        self.set_caption("Keep the same object visible in the economic and analytical views.")
        economic_view = ChannelDecomposition(
            (
                ("observed input", theme.blue),
                ("behavioral margin", theme.green),
            ),
            outcome="target",
            theme=theme,
        )
        analytical_view = object_badge(theme, "estimable target")
        application = LinkedViews(
            economic_view,
            analytical_view,
            left_title="economic interpretation",
            right_title="usable output",
            relation="one object · one result · one application",
            theme=theme,
        ).scale(1.02).move_to([0, -0.30, 0])
        self.play(FadeIn(application), run_time=0.80)
        self.wait(1.8)
        self.clear_stage(application, persistent, run_time=0.35)

        self.next_section("conclusion")
        self.show_title("Return to the opening problem")
        self.set_caption(
            "Close with what the method makes possible and the conditions it requires."
        )
        solved = object_badge(theme, "target recovered under stated conditions").move_to(
            [0, 0.10, 0]
        )
        self.play(FadeIn(solved, shift=UP * 0.08), run_time=0.70)
        self.wait(2.0)
