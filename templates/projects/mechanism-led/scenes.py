"""Paper-independent skeleton for a mechanism-led research explainer."""

from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    RoundedRectangle,
    VGroup,
)

from econ_manim import (
    CausalChain,
    DivergingBarChart,
    EquationBuild,
    ResearchScene,
    fit_prose_text,
    read_csv_rows,
)

COMPARISON_ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "comparison.csv",
    required_columns=("label", "value"),
)


def system_diagram(theme):
    positions = (LEFT * 3.6, UP * 1.15, DOWN * 1.15, RIGHT * 3.6)
    labels = ("change", "channel A", "channel B", "outcome")
    colors = (theme.orange, theme.blue, theme.green, theme.foreground)
    nodes = VGroup()
    node_labels = VGroup()
    for position, label, color in zip(positions, labels, colors, strict=True):
        node = RoundedRectangle(
            width=1.55,
            height=0.66,
            corner_radius=0.14,
            stroke_color=color,
            stroke_width=2,
            fill_color=theme.card,
            fill_opacity=1,
        ).move_to(position)
        text = fit_prose_text(
            label,
            max_width=1.25,
            font_size=20,
            min_font_size=11,
            color=color,
        )
        text.move_to(node)
        nodes.add(node)
        node_labels.add(text)
    edges = VGroup(
        Line(nodes[0].get_right(), nodes[1].get_left(), color=theme.grid),
        Line(nodes[0].get_right(), nodes[2].get_left(), color=theme.grid),
        Line(nodes[1].get_right(), nodes[3].get_left(), color=theme.grid),
        Line(nodes[2].get_right(), nodes[3].get_left(), color=theme.grid),
    )
    return VGroup(edges, nodes, node_labels), nodes, edges


class MechanismExplainer(ResearchScene):
    def construct(self):
        theme = self.theme
        self.next_section("opening")
        self.show_title("How does one change propagate?")
        self.set_caption("Replace the placeholders with the paper's intervention and outcome.")
        chain = CausalChain(
            (
                ("change", theme.orange),
                ("responses", theme.blue),
                ("feedback", theme.green),
                ("outcome", theme.foreground),
            ),
            theme=theme,
        ).scale(1.12).move_to([0, 0.15, 0])
        self.play(FadeIn(chain, shift=UP * 0.08), run_time=0.8)
        self.wait(2.0)
        self.clear_stage(chain, run_time=0.35)

        self.next_section("system")
        self.show_title("Build the baseline system")
        self.set_caption("Illustrative geometry · retain only objects required by the mechanism.")
        system, nodes, edges = system_diagram(theme)
        self.play(Create(edges), run_time=0.8)
        self.play(FadeIn(VGroup(nodes, system[2])), run_time=0.7)
        self.wait(1.6)

        self.next_section("perturbation")
        self.show_title("Change one persistent object")
        self.set_caption("Trace each economic channel without resetting the viewer's mental map.")
        halo = Circle(
            radius=0.64,
            stroke_color=theme.orange,
            stroke_width=3,
        ).move_to(nodes[0])
        route_a = Arrow(
            nodes[0].get_right(),
            nodes[1].get_left(),
            buff=0.06,
            color=theme.blue,
            stroke_width=3,
            tip_length=0.14,
        )
        route_b = Arrow(
            nodes[0].get_right(),
            nodes[2].get_left(),
            buff=0.06,
            color=theme.green,
            stroke_width=3,
            tip_length=0.14,
        )
        self.play(Create(halo), Create(route_a), run_time=0.8)
        self.play(Create(route_b), Indicate(nodes[3], color=theme.foreground), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(VGroup(system, halo, route_a, route_b)), run_time=0.4)

        self.next_section("comparison")
        self.show_title("Compare every case with one benchmark")
        self.set_caption("Illustrative values only · replace them and document the source.")
        comparison = DivergingBarChart(
            tuple(
                (
                    row["label"],
                    float(row["value"]),
                    theme.blue if float(row["value"]) >= 0 else theme.green,
                )
                for row in COMPARISON_ROWS
            ),
            benchmark_label="preferred case",
            left_label="smaller",
            right_label="larger",
            theme=theme,
        ).scale(1.20).move_to([0, -0.10, 0])
        self.play(FadeIn(comparison), run_time=0.8)
        self.wait(2.0)
        self.clear_stage(comparison, run_time=0.35)

        self.next_section("synthesis")
        self.show_title("Reuse the mechanism in the conclusion")
        self.set_caption("Words first · introduce formal notation only when it adds information.")
        equation = EquationBuild(
            (
                ("direct channel", theme.blue),
                ("feedback channel", theme.green),
            ),
            lhs="outcome",
            theme=theme,
        ).scale(1.06).move_to([0, 0.10, 0])
        self.play(FadeIn(VGroup(equation.lhs, equation.equals)), run_time=0.6)
        self.play(FadeIn(equation.terms[0]), run_time=0.5)
        self.play(FadeIn(equation.operators), FadeIn(equation.terms[1]), run_time=0.5)
        self.wait(2.0)
