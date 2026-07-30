"""Paper-independent gallery of reusable economics visuals."""

from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    Create,
    Dot,
    FadeIn,
    GrowFromEdge,
    Line,
    VGroup,
)

from econ_manim import (
    CausalChain,
    ChannelDecomposition,
    ChoiceMap,
    CityLaborMarket,
    CoefficientPlot,
    DivergingBarChart,
    EquationBuild,
    ImpulseResponsePlot,
    LinkedViews,
    PathFlow,
    ResearchScene,
    ResultTable,
    ShockDistribution,
    WorkerToken,
    adjustment_route,
    read_csv_rows,
)

ROOT = Path(__file__).parent
COMPARISON_ROWS = read_csv_rows(
    ROOT / "data" / "comparison.csv",
    required_columns=("label", "value", "color_role"),
)
EVIDENCE_ROWS = read_csv_rows(
    ROOT / "data" / "evidence.csv",
    required_columns=("kind", "label", "horizon", "estimate", "lower", "upper", "color_role"),
)
DECOMPOSITION_ROWS = read_csv_rows(
    ROOT / "data" / "decomposition.csv",
    required_columns=("label", "label_color", "direct", "indirect", "total"),
)


def _network_view(theme):
    points = (
        [-1.65, 0.55, 0],
        [-0.55, -0.45, 0],
        [0.55, -0.45, 0],
        [1.65, 0.55, 0],
    )
    nodes = VGroup(*[Dot(point, radius=0.11, color=theme.foreground) for point in points])
    edges = VGroup(
        Line(points[0], points[1], color=theme.grid, stroke_width=2.0),
        Line(points[1], points[2], color=theme.grid, stroke_width=2.0),
        Line(points[2], points[3], color=theme.grid, stroke_width=2.0),
        Line(points[0], points[2], color=theme.grid, stroke_width=1.5),
    )
    return VGroup(edges, nodes), edges[1]


def _coefficient_plot(theme):
    rows = [row for row in EVIDENCE_ROWS if row["kind"] == "coefficient"]
    return CoefficientPlot(
        tuple(
            (
                row["label"],
                float(row["estimate"]),
                float(row["lower"]),
                float(row["upper"]),
                getattr(theme, row["color_role"]),
            )
            for row in rows
        ),
        x_label="same estimand and scale",
        theme=theme,
    )


def _impulse_response(theme):
    rows = [row for row in EVIDENCE_ROWS if row["kind"] == "irf"]
    horizons = tuple(float(row["horizon"]) for row in rows)
    estimates = tuple(float(row["estimate"]) for row in rows)
    lower = tuple(float(row["lower"]) for row in rows)
    upper = tuple(float(row["upper"]) for row in rows)
    return ImpulseResponsePlot(
        {"response": (estimates, theme.blue)},
        horizons=horizons,
        confidence_intervals={"response": (lower, upper)},
        event_time=0,
        x_label="horizon",
        theme=theme,
    )


class FormatGallery(ResearchScene):
    def construct(self):
        theme = self.theme

        self.next_section("agents-and-choices")
        self.show_title("Agents and choices")
        self.set_caption("Use a neutral token unless the paper requires a domain-specific object.")
        menu = ChoiceMap(
            (
                ("option A", theme.blue),
                ("option B", theme.green),
                ("wait or exit", theme.orange),
            ),
            agent_label="decision maker",
            theme=theme,
        ).move_to([0, 0.05, 0])
        self.play(FadeIn(menu.origin), run_time=0.40)
        self.play(
            FadeIn(menu.routes),
            FadeIn(menu[2]),
            run_time=0.70,
        )
        self.wait(1.2)
        self.clear_stage(menu)

        self.next_section("domain-extension")
        self.show_title("Optional domain extensions")
        self.set_caption("Specialized objects are examples, not assumptions built into the starter.")
        city_a = CityLaborMarket(
            "market A",
            (2, 2, 1, 2),
            radius=1.30,
            accent=theme.blue,
            theme=theme,
        ).scale(0.78).move_to(LEFT * 3.20)
        city_b = CityLaborMarket(
            "market B",
            (1, 2, 2, 1),
            radius=1.30,
            accent=theme.green,
            theme=theme,
        ).scale(0.78).move_to(RIGHT * 3.20)
        worker = WorkerToken(label="worker", theme=theme).scale(0.82).move_to([0, 1.15, 0])
        route = adjustment_route(
            city_a.get_right(),
            city_b.get_left(),
            label="across markets",
            color=theme.orange,
            label_direction=DOWN,
        )
        domain = VGroup(city_a, city_b, worker, route).move_to([0, -0.05, 0])
        self.play(FadeIn(VGroup(city_a, city_b, worker)), run_time=0.65)
        self.play(Create(route[0]), FadeIn(route[1]), run_time=0.55)
        self.wait(1.2)
        self.clear_stage(domain)

        self.next_section("path-flow")
        self.show_title("Trace movement through one stable system")
        self.set_caption("PathFlow supports straight, curved, and multi-segment adjustment routes.")
        nodes = VGroup(
            Dot([-4.0, 0.2, 0], radius=0.14, color=theme.foreground),
            Dot([-1.2, 0.2, 0], radius=0.14, color=theme.foreground),
            Dot([1.0, -0.6, 0], radius=0.14, color=theme.foreground),
            Dot([4.0, 0.4, 0], radius=0.14, color=theme.foreground),
        )
        direct = PathFlow(
            ((-4.0, 0.2, 0), (-1.2, 0.2, 0)),
            label="local response",
            color=theme.blue,
            theme=theme,
        )
        indirect = PathFlow(
            ((-1.2, 0.2, 0), (1.0, -0.6, 0), (4.0, 0.4, 0)),
            label="system response",
            color=theme.orange,
            curved=True,
            theme=theme,
        )
        flows = VGroup(nodes, direct, indirect)
        self.play(FadeIn(nodes), Create(direct.path), FadeIn(direct.label), run_time=0.60)
        self.play(direct.travel_animation(run_time=0.70))
        self.play(Create(indirect.path), FadeIn(indirect.label), run_time=0.60)
        self.play(indirect.travel_animation(run_time=0.90))
        self.wait(1.0)
        self.clear_stage(flows)

        self.next_section("causal-chain")
        self.show_title("Build one causal chain")
        self.set_caption("Keep the labels economic and reuse them in the conclusion.")
        chain = CausalChain(
            (
                ("intervention", theme.orange),
                ("choices adjust", theme.blue),
                ("spillovers", theme.green),
                ("welfare", theme.foreground),
            ),
            theme=theme,
        ).move_to([0, 0.10, 0])
        self.play(FadeIn(chain.nodes[0]), run_time=0.35)
        for arrow, node in zip(chain.arrows, chain.nodes[1:], strict=True):
            self.play(Create(arrow), FadeIn(node, shift=RIGHT * 0.05), run_time=0.45)
        self.wait(1.1)
        self.clear_stage(chain)

        self.next_section("channels")
        self.show_title("Separate channels before recombining them")
        self.set_caption("A conceptual channel is not automatically a separately identified effect.")
        channels = ChannelDecomposition(
            (
                ("direct response", theme.blue),
                ("market spillover", theme.green),
                ("resource cost", theme.orange),
            ),
            outcome="change in welfare",
            theme=theme,
        ).move_to([0, 0.05, 0])
        self.play(FadeIn(channels.outcome), run_time=0.35)
        for channel, arrow in zip(channels.channels, channels.arrows, strict=True):
            self.play(FadeIn(channel), Create(arrow), run_time=0.45)
        self.wait(1.1)
        self.clear_stage(channels)

        self.next_section("linked-views")
        self.show_title("Synchronize an economic and analytical view")
        self.set_caption("Reveal the same margin in both views with the same semantic color.")
        network, treated_edge = _network_view(theme)
        equation = EquationBuild(
            (
                ("direct response", theme.blue),
                ("spillovers", theme.green),
                ("resource cost", theme.orange),
            ),
            lhs="welfare",
            operators=("+", "-"),
            theme=theme,
        )
        linked = LinkedViews(
            network,
            equation,
            left_title="economic system",
            right_title="economic summary",
            relation="one state · two representations",
            theme=theme,
        ).move_to([0, -0.05, 0])
        treated = treated_edge.copy().set_stroke(color=theme.orange, width=7.0)
        self.play(FadeIn(linked), Create(treated), run_time=0.75)
        self.wait(1.4)
        self.clear_stage(linked, treated)

        self.next_section("empirical-evidence")
        self.show_title("Keep empirical comparisons on a common frame")
        self.set_caption("Illustrative values · state the estimand, horizon, units, and confidence level.")
        evidence = LinkedViews(
            _coefficient_plot(theme),
            _impulse_response(theme),
            left_title="coefficient intervals",
            right_title="dynamic response",
            relation="same estimand · different empirical views",
            theme=theme,
        ).scale(0.91).move_to([0, -0.05, 0])
        self.play(FadeIn(evidence), run_time=0.75)
        self.wait(1.6)
        self.clear_stage(evidence)

        self.next_section("distribution")
        self.show_title("Show realized variation without decorative bars")
        self.set_caption("Illustrative observations · direct labels should carry units and sample meaning.")
        shock_rows = [row for row in EVIDENCE_ROWS if row["kind"] == "shock"]
        distribution = ShockDistribution(
            tuple(
                (
                    float(row["estimate"]),
                    getattr(theme, row["color_role"]),
                )
                for row in shock_rows
            ),
            x_range=(-0.6, 0.6, 0.2),
            label="illustrative realized variation",
            theme=theme,
        ).move_to([0, 0.0, 0])
        self.play(Create(distribution.axis), FadeIn(distribution[2]), run_time=0.55)
        self.play(FadeIn(distribution.dots), run_time=0.55)
        self.wait(1.2)
        self.clear_stage(distribution)

        self.next_section("benchmark")
        self.show_title("Compare restrictions with one benchmark")
        self.set_caption("Illustrative values · the zero line defines the preferred case.")
        comparison = DivergingBarChart(
            tuple(
                (
                    row["label"],
                    float(row["value"]),
                    getattr(theme, row["color_role"]),
                )
                for row in COMPARISON_ROWS
            ),
            benchmark_label="full model",
            left_label="smaller implied gain",
            right_label="larger implied gain",
            theme=theme,
        ).move_to([0, -0.05, 0])
        self.play(
            Create(comparison.zero),
            FadeIn(comparison.benchmark),
            FadeIn(comparison.side_labels),
            run_time=0.55,
        )
        for row, source in zip(comparison.rows, COMPARISON_ROWS, strict=True):
            label, bar, amount = row
            value = float(source["value"])
            self.play(
                FadeIn(label),
                GrowFromEdge(bar, LEFT if value >= 0 else RIGHT),
                FadeIn(amount),
                run_time=0.45,
            )
        self.wait(1.2)
        self.clear_stage(comparison)

        self.next_section("result-table")
        self.show_title("Reserve tables for compact decompositions")
        self.set_caption("Illustrative values · every displayed cell belongs in the project manifest.")
        table = ResultTable(
            (
                ("direct", theme.blue),
                ("indirect", theme.green),
                ("total", theme.foreground),
            ),
            tuple(
                (
                    row["label"],
                    getattr(theme, row["label_color"]),
                    (
                        float(row["direct"]),
                        float(row["indirect"]),
                        float(row["total"]),
                    ),
                )
                for row in DECOMPOSITION_ROWS
            ),
            theme=theme,
        ).move_to([0, 0.0, 0])
        self.play(FadeIn(table.headers), Create(table.rule), run_time=0.55)
        for row in table.rows:
            self.play(FadeIn(row), run_time=0.45)
        self.wait(1.4)
