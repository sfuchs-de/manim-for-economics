import shutil

import pytest

from econ_manim import (
    ECON_DARK,
    AgentToken,
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
    ResultTable,
    ShockDistribution,
    WorkerToken,
    assert_within_frame,
)


def test_city_is_symmetric_and_counts_workers():
    city = CityLaborMarket("city", (2, 2, 2, 2))
    assert len(city.cells) == 4
    assert [len(group) for group in city.workers] == [2, 2, 2, 2]
    assert_within_frame(city)


def test_worker_token_constructs():
    worker = WorkerToken(label="worker")
    assert len(worker) == 2
    assert_within_frame(worker)


def test_domain_neutral_agent_and_choice_map_construct():
    agent = AgentToken(label="firm")
    menu = ChoiceMap(
        (
            ("adopt", ECON_DARK.green),
            ("wait", ECON_DARK.blue),
            ("exit", ECON_DARK.orange),
        ),
        agent_label="firm",
    )
    assert len(menu.routes) == 3
    assert len(menu.nodes) == 3
    assert menu.origin.get_center()[0] < menu.nodes.get_center()[0]
    for mobject in (agent, menu):
        assert_within_frame(mobject)


def test_choice_map_rejects_an_unreadable_number_of_alternatives():
    with pytest.raises(ValueError, match="between two and four"):
        ChoiceMap((("only", ECON_DARK.blue),))


def test_charts_construct_with_small_inputs():
    irf = ImpulseResponsePlot(
        {
            "low HHI": ([0.0, -0.2, -0.3], ECON_DARK.green),
            "high HHI": ([0.0, -0.4, -0.7], ECON_DARK.orange),
        }
    )
    table = ResultTable(
        (
            ("direct", ECON_DARK.blue),
            ("second", ECON_DARK.green),
            ("total", ECON_DARK.foreground),
        ),
        (("diversified", ECON_DARK.green, (-1.0, -0.1, -1.1)),),
    )
    for mobject in (irf, table):
        assert mobject.width > 0
        assert mobject.height > 0


def test_impulse_response_supports_horizons_bands_and_event_time():
    irf = ImpulseResponsePlot(
        {"response": ([0.0, -0.2, -0.1], ECON_DARK.blue)},
        horizons=(-1, 0, 2),
        confidence_intervals={
            "response": ([-0.1, -0.4, -0.3], [0.1, 0.0, 0.1]),
        },
        event_time=0,
    )
    assert len(irf.bands) == 1
    assert irf.event.height > 0
    assert len(irf.lines) == 1


def test_impulse_response_rejects_invalid_confidence_intervals():
    with pytest.raises(ValueError, match="must contain"):
        ImpulseResponsePlot(
            {"response": ([0.0, -0.2], ECON_DARK.blue)},
            confidence_intervals={"response": ([0.1, -0.3], [0.2, -0.1])},
        )


def test_coefficient_plot_constructs_and_validates_bounds():
    plot = CoefficientPlot(
        (
            ("group A", -0.2, -0.3, -0.1, ECON_DARK.blue),
            ("group B", 0.1, -0.1, 0.3, ECON_DARK.orange),
        )
    )
    assert len(plot.rows) == 2
    assert len(plot.intervals) == 2
    assert plot.reference.height > 0
    with pytest.raises(ValueError, match="must contain"):
        CoefficientPlot((("invalid", 0.5, 0.6, 0.7, ECON_DARK.blue),))


def test_path_flow_supports_straight_curved_and_segmented_routes():
    straight = PathFlow(((-2, 0, 0), (2, 0, 0)), label="direct")
    curved = PathFlow(((-2, 0, 0), (2, 0, 0)), curved=True)
    segmented = PathFlow(((-2, 0, 0), (0, 1, 0), (2, 0, 0)))
    for flow in (straight, curved, segmented):
        assert flow.path.width > 0
        assert flow.token.get_center()[0] == pytest.approx(flow.path.get_start()[0])
        assert flow.travel_animation(run_time=0.5).run_time == 0.5


def test_channel_decomposition_exposes_incremental_parts():
    decomposition = ChannelDecomposition(
        (
            ("direct", ECON_DARK.blue),
            ("spillover", ECON_DARK.green),
            ("cost", ECON_DARK.orange),
        ),
        outcome="welfare",
    )
    assert len(decomposition.channels) == 3
    assert len(decomposition.arrows) == 3
    assert decomposition.channels.get_center()[0] < decomposition.outcome.get_center()[0]


def test_visual_formats_construct_without_hidden_data():
    chain = CausalChain(
        (
            ("shock", ECON_DARK.orange),
            ("choices", ECON_DARK.blue),
            ("welfare", ECON_DARK.green),
        )
    )
    chart = DivergingBarChart(
        (
            ("restriction A", 40, ECON_DARK.orange),
            ("restriction B", -25, ECON_DARK.blue),
        )
    )
    views = LinkedViews(
        CityLaborMarket("market", (2, 2, 2, 2)),
        chart,
        left_title="economic system",
        right_title="benchmark comparison",
    )
    assert len(chain.nodes) == 3
    assert len(chain.arrows) == 2
    assert len(chart.rows) == 2
    assert views.left_group.get_center()[0] < views.right_group.get_center()[0]
    relation_line = views.relation[0]
    assert relation_line.get_start()[1] == pytest.approx(relation_line.get_end()[1])
    for mobject in (chain, chart, views):
        assert mobject.width > 0
        assert mobject.height > 0
        assert_within_frame(mobject)
    for row in chart.rows:
        label, _, amount = row
        assert label.get_right()[0] < amount.get_left()[0]


@pytest.mark.skipif(shutil.which("latex") is None, reason="MathTex requires LaTeX")
def test_equation_build_constructs_with_latex():
    equation = EquationBuild(
        [
            ("first order", ECON_DARK.blue),
            ("spillovers", ECON_DARK.green),
            ("congestion", ECON_DARK.orange),
        ],
        operators=("+", "-"),
    )
    assert len(equation.operators) == 2
    assert equation.width > 0
    assert equation.height > 0
    shocks = ShockDistribution([(-0.2, ECON_DARK.orange), (0.3, ECON_DARK.green)])
    assert shocks.width > 0
    assert shocks.height > 0


@pytest.mark.skipif(shutil.which("latex") is None, reason="MathTex requires LaTeX")
def test_equation_build_rejects_wrong_operator_count():
    with pytest.raises(ValueError, match="operators"):
        EquationBuild(
            [
                ("first order", ECON_DARK.blue),
                ("second order", ECON_DARK.green),
            ],
            operators=("+", "-"),
        )
