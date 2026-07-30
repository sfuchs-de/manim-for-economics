"""Small gallery of visual formats distilled from two production explainers."""

from manim import (
    LEFT,
    RIGHT,
    UP,
    Create,
    Dot,
    FadeIn,
    GrowFromEdge,
    Line,
    VGroup,
)

from econ_manim import (
    ECON_DARK,
    CausalChain,
    DivergingBarChart,
    EquationBuild,
    LinkedViews,
    ResearchScene,
)


def _network_view():
    points = (
        [-1.65, 0.55, 0],
        [-0.55, -0.45, 0],
        [0.55, -0.45, 0],
        [1.65, 0.55, 0],
    )
    nodes = VGroup(
        *[
            Dot(point, radius=0.11, color=ECON_DARK.foreground)
            for point in points
        ]
    )
    edges = VGroup(
        Line(points[0], points[1], color=ECON_DARK.grid, stroke_width=2.0),
        Line(points[1], points[2], color=ECON_DARK.grid, stroke_width=2.0),
        Line(points[2], points[3], color=ECON_DARK.grid, stroke_width=2.0),
        Line(points[0], points[2], color=ECON_DARK.grid, stroke_width=1.5),
    )
    return VGroup(edges, nodes), edges[1]


class FormatGallery(ResearchScene):
    def construct(self):
        self.next_section("causal-chain")
        self.show_title("Format 1 · build one causal chain")
        self.set_caption(
            "Keep the labels economic: intervention, behavioral response, equilibrium response, welfare."
        )
        chain = CausalChain(
            (
                ("local intervention", ECON_DARK.orange),
                ("choices adjust", ECON_DARK.blue),
                ("spillovers propagate", ECON_DARK.green),
                ("welfare changes", ECON_DARK.foreground),
            )
        ).move_to([0, 0.15, 0])
        self.play(FadeIn(chain.nodes[0], shift=UP * 0.06), run_time=0.45)
        for arrow, node in zip(chain.arrows, chain.nodes[1:], strict=True):
            self.play(
                Create(arrow),
                FadeIn(node, shift=RIGHT * 0.06),
                run_time=0.55,
            )
        self.wait(1.4)
        self.clear_stage(chain)

        self.next_section("linked-views")
        self.show_title("Format 2 · synchronize two views")
        self.set_caption(
            "Reuse the same color and timing when a mechanism appears in the system and the equation."
        )
        network, treated_edge = _network_view()
        equation = EquationBuild(
            (
                ("direct response", ECON_DARK.blue),
                ("spillovers", ECON_DARK.green),
                ("congestion", ECON_DARK.orange),
            ),
            lhs="welfare",
            operators=("+", "-"),
        )
        pair = LinkedViews(
            network,
            equation,
            left_title="economic system",
            right_title="economic summary",
            relation="one intervention · two synchronized representations",
        ).move_to([0, -0.05, 0])
        treated_overlay = treated_edge.copy().set_stroke(
            color=ECON_DARK.orange,
            width=7.0,
        )
        self.play(FadeIn(pair.headings), FadeIn(pair.relation), FadeIn(network), run_time=0.65)
        self.play(
            FadeIn(VGroup(equation.lhs, equation.equals)),
            Create(treated_overlay),
            run_time=0.65,
        )
        self.play(FadeIn(equation.terms[0]), run_time=0.45)
        self.play(
            FadeIn(equation.operators[0]),
            FadeIn(equation.terms[1]),
            run_time=0.45,
        )
        self.play(
            FadeIn(equation.operators[1]),
            FadeIn(equation.terms[2]),
            run_time=0.45,
        )
        self.wait(1.5)
        self.clear_stage(pair, treated_overlay)

        self.next_section("benchmark-comparison")
        self.show_title("Format 3 · compare with a benchmark")
        self.set_caption(
            "Illustrative values: the zero line is the full model; each row changes one assumption."
        )
        chart = DivergingBarChart(
            (
                ("restriction A", 40, ECON_DARK.orange),
                ("restriction B", 12, ECON_DARK.orange),
                ("restriction C", -25, ECON_DARK.blue),
            ),
            benchmark_label="full model",
            left_label="smaller implied gain",
            right_label="larger implied gain",
        ).move_to([0, -0.05, 0])
        self.play(
            Create(chart.zero),
            FadeIn(chart.benchmark),
            FadeIn(chart.side_labels),
            run_time=0.6,
        )
        for row, value in zip(chart.rows, (40, 12, -25), strict=True):
            label, bar, amount = row
            self.play(
                FadeIn(label),
                GrowFromEdge(bar, LEFT if value >= 0 else RIGHT),
                FadeIn(amount),
                run_time=0.55,
            )
        self.wait(2.0)
