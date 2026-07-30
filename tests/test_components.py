import shutil

import pytest

from econ_manim import (
    ECON_DARK,
    AgentToken,
    CausalChain,
    ChoiceMap,
    CityLaborMarket,
    DivergingBarChart,
    EquationBuild,
    ImpulseResponsePlot,
    LinkedViews,
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
    for mobject in (chain, chart, views):
        assert mobject.width > 0
        assert mobject.height > 0
        assert_within_frame(mobject)


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
