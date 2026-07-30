import shutil

import pytest

from econ_manim import (
    ECON_DARK,
    CityLaborMarket,
    EquationBuild,
    ImpulseResponsePlot,
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


@pytest.mark.skipif(shutil.which("latex") is None, reason="MathTex requires LaTeX")
def test_equation_build_constructs_with_latex():
    equation = EquationBuild(
        [
            ("first order", ECON_DARK.blue),
            ("second order", ECON_DARK.green),
        ]
    )
    assert equation.width > 0
    assert equation.height > 0
    shocks = ShockDistribution([(-0.2, ECON_DARK.orange), (0.3, ECON_DARK.green)])
    assert shocks.width > 0
    assert shocks.height > 0
