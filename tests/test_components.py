import json
import shutil

import pytest

from econ_manim import (
    ECON_DARK,
    IVORY,
    MIDNIGHT,
    AgentToken,
    CausalChain,
    ChannelDecomposition,
    ChoiceMap,
    CityLaborMarket,
    CoefficientPlot,
    DivergingBarChart,
    EquationBuild,
    EvolvingScatterPlot,
    GeographicNetworkMap,
    ImpulseResponsePlot,
    LinkedViews,
    NetworkInset,
    NetworkLink,
    PaperCodeEndSlate,
    PathFlow,
    ResultTable,
    ScatterObservation,
    SelectedRankHistoryPanel,
    SelectedRankPanel,
    SelectedRankProjections,
    ShockDistribution,
    WorkerToken,
    assert_within_frame,
    ranked_value_groups,
    read_geojson_regions,
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


@pytest.mark.parametrize("theme", (MIDNIGHT, IVORY))
def test_paper_code_end_slate_constructs_in_both_themes(theme):
    slate = PaperCodeEndSlate(
        paper_title="A Paper\nwith a Short Title",
        paper_authors="Author One · Author Two",
        paper_status="Working paper\nforthcoming",
        package_name="ResearchPackage.jl",
        package_summary="Reusable code, documentation,\nand examples",
        package_url="github.com/example/ResearchPackage.jl",
        invitation="Apply the method to your own setting.",
        theme=theme,
    )
    assert slate.paper_resource.get_center()[0] < 0
    assert slate.code_resource.get_center()[0] > 0
    assert slate.divider.get_start()[0] == pytest.approx(0)
    assert slate.divider.get_end()[0] == pytest.approx(0)
    assert_within_frame(slate)


def test_paper_code_end_slate_rejects_empty_required_fields():
    with pytest.raises(ValueError, match="cannot be empty"):
        PaperCodeEndSlate(
            paper_title="",
            paper_authors="Author",
            paper_status="forthcoming",
            package_name="Package.jl",
            package_summary="summary",
            package_url="example.com/package",
        )


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


def test_evolving_scatter_links_states_ranks_and_network_geometry():
    observations = (
        ScatterObservation(
            "a",
            0.2,
            {"traditional": 0.2, "spatial": 0.3, "extended": 0.12},
            "A--B",
        ),
        ScatterObservation(
            "b",
            0.4,
            {"traditional": 0.4, "spatial": 0.25, "extended": 0.18},
            "C--D",
        ),
    )
    scatter = EvolvingScatterPlot(
        observations,
        ("traditional", "spatial", "extended"),
        selected_colors={"a": ECON_DARK.orange, "b": ECON_DARK.green},
        state_colors={
            "traditional": {"a": "#111111", "b": "#222222"},
            "spatial": {"a": "#333333", "b": "#444444"},
            "extended": {"a": "#555555", "b": "#666666"},
        },
        x_range=(0, 0.5, 0.1),
    )
    ranks = SelectedRankPanel(scatter, {"a": "A--B", "b": "C--D"})
    rank_history = SelectedRankHistoryPanel(
        scatter,
        {"a": "A--B", "b": "C--D"},
        state_headers={"traditional": "Traditional", "spatial": "Spatial"},
    )
    projections = SelectedRankProjections(scatter, ("a", "b"))
    network = NetworkInset(
        (
            NetworkLink("a", (-100, 35), (-98, 36)),
            NetworkLink("b", (-98, 36), (-95, 34)),
        ),
        selected_colors={"a": ECON_DARK.orange, "b": ECON_DARK.green},
        values={"a": 0.1, "b": 0.8},
        value_range=(0.0, 1.0),
    )

    assert scatter.ranks("traditional") == {"b": 1, "a": 2}
    assert scatter.ranks("spatial") == {"a": 1, "b": 2}
    assert scatter.dot_layers(("b", "a"))[0] is scatter.dots_by_id["b"]
    assert len(scatter.transition_lines("spatial")) == 2
    assert scatter.animate_to("spatial").run_time == pytest.approx(1.6)
    assert ranks.animate_to("spatial").run_time == pytest.approx(0.7)
    assert rank_history.columns_by_state["traditional"][0].text == "#2"
    assert rank_history.columns_by_state["spatial"][0].text == "#1"
    assert rank_history.headers_by_state["traditional"].text == "Traditional"
    assert len(projections) == 2
    assert projections[0][2].text == "#2"
    assert projections.animate_to("spatial").run_time == pytest.approx(1.6)
    assert projections.current_state == "spatial"
    assert network.isolate("a")[1][0].get_stroke_opacity() == pytest.approx(1.0)
    assert network.base_by_id["b"].get_stroke_width() > network.base_by_id["a"].get_stroke_width()


def test_ranked_value_groups_are_balanced_and_deterministic():
    groups = ranked_value_groups(
        {"d": 1.0, "b": 3.0, "a": 3.0, "c": 2.0, "e": 0.0},
        groups=2,
    )

    assert groups == (("a", "b", "c"), ("d", "e"))
    assert ranked_value_groups(
        {"a": 1.0, "b": 2.0, "c": 3.0},
        groups=3,
        descending=False,
    ) == (("a",), ("b",), ("c",))


def test_geographic_network_map_reads_geojson_and_encodes_links(tmp_path):
    geojson = tmp_path / "regions.geojson"
    geojson.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"code": "west"},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {"code": "east"},
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]
                            ],
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    regions = read_geojson_regions(geojson, identifier_property="code")
    links = (
        NetworkLink("low", (0.2, 0.3), (0.8, 0.7)),
        NetworkLink("high", (1.2, 0.3), (1.8, 0.7)),
    )
    map_view = GeographicNetworkMap(
        regions,
        links,
        values={"low": 1.0, "high": 8.0},
        color_values={"low": 1.0, "high": 2.0},
        extent=(0.0, 2.0, 0.0, 1.0),
        value_range=(0.0, 10.0),
        color_range=(1.0, 2.0),
        selected_colors={"high": ECON_DARK.orange},
        legend_ticks=(0.0, 5.0, 10.0),
    )

    assert len(regions) == 2
    assert len(map_view.base_links) == 2
    projected = map_view.project_point((1.0, 0.5))
    assert tuple(projected) == pytest.approx((0.0, 0.0, 0.0))
    with pytest.raises(ValueError, match="finite"):
        map_view.project_point((float("nan"), 0.5))
    assert map_view.base_by_id["high"].get_stroke_width() > map_view.base_by_id[
        "low"
    ].get_stroke_width()
    underlays, encoded = map_view.link_layers(("high", "low"))
    assert underlays[0] is map_view.underlay_by_id["high"]
    assert encoded[1] is map_view.base_by_id["low"]
    with pytest.raises(ValueError, match="unique"):
        map_view.link_layers(("high", "high"))
    with pytest.raises(ValueError, match="unknown"):
        map_view.link_layers(("missing",))
    markers = map_view.location_markers(
        {"origin": (0.2, 0.3), "destination": (1.8, 0.7)},
        color=ECON_DARK.green,
    )
    assert len(markers) == 2
    assert markers.marker_by_id["origin"].get_center() == pytest.approx(
        map_view.project_point((0.2, 0.3))
    )
    map_view.shift([0.35, -0.20, 0.0])
    shifted_markers = map_view.location_markers({"origin": (0.2, 0.3)})
    assert shifted_markers.marker_by_id["origin"].get_center() == pytest.approx(
        map_view.base_by_id["low"].get_start()
    )
    skeleton = map_view.network_skeleton(opacity=0.35)
    assert len(skeleton) == 2
    assert skeleton.skeleton_by_id["low"] is not map_view.base_by_id["low"]
    assert skeleton.skeleton_by_id["low"].get_stroke_opacity() == pytest.approx(0.35)
    with pytest.raises(ValueError, match="radius"):
        map_view.location_markers({"origin": (0.2, 0.3)}, radius=0)
    with pytest.raises(ValueError, match="opacity"):
        map_view.network_skeleton(opacity=1.1)
    assert map_view.animate_values({"low": 9.0, "high": 2.0}).run_time == pytest.approx(
        1.6
    )
    assert map_view.color_values == {"low": 1.0, "high": 2.0}
    assert map_view.animate_values(
        {"low": 2.0, "high": 9.0},
        color_values={"low": 2.0, "high": 1.0},
    ).run_time == pytest.approx(1.6)
    assert map_view.color_values == {"low": 2.0, "high": 1.0}
    assert map_view.isolate("high")[5][0].get_stroke_opacity() == pytest.approx(1.0)


def test_evolving_scatter_rejects_inconsistent_inputs():
    with pytest.raises(ValueError, match="missing states"):
        EvolvingScatterPlot(
            (ScatterObservation("a", 0.2, {"traditional": 0.2}),),
            ("traditional", "extended"),
        )
    with pytest.raises(ValueError, match="must be unique"):
        NetworkInset(
            (
                NetworkLink("a", (0, 0), (1, 1)),
                NetworkLink("a", (1, 1), (2, 2)),
            )
        )
    with pytest.raises(ValueError, match="cover exactly"):
        NetworkInset(
            (
                NetworkLink("a", (0, 0), (1, 1)),
                NetworkLink("b", (1, 1), (2, 2)),
            ),
            values={"a": 0.2},
        )


@pytest.mark.parametrize("theme", (MIDNIGHT, IVORY))
def test_v020_components_construct_in_both_themes(theme):
    components = (
        PathFlow(((-2, 0, 0), (2, 0, 0)), label="response", theme=theme),
        ChannelDecomposition(
            (("direct", theme.blue), ("spillover", theme.green)),
            outcome="outcome",
            theme=theme,
        ),
        CoefficientPlot(
            (("estimate", -0.2, -0.3, -0.1, theme.blue),),
            theme=theme,
        ),
        ImpulseResponsePlot(
            {"response": ([0.0, -0.2, -0.1], theme.blue)},
            horizons=(-1, 0, 1),
            confidence_intervals={
                "response": ([-0.1, -0.4, -0.3], [0.1, 0.0, 0.1]),
            },
            event_time=0,
            theme=theme,
        ),
    )

    for component in components:
        assert component.width > 0
        assert component.height > 0
        assert_within_frame(component)


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
    traditional_brace = equation.rhs_brace(
        "traditional",
        start=0,
        stop=1,
        color=ECON_DARK.blue,
    )
    extended_brace = equation.rhs_brace(
        "extended",
        color=ECON_DARK.green,
    )
    assert len(traditional_brace.target) == 1
    assert len(extended_brace.target) == 5
    assert traditional_brace.brace.get_left()[0] > equation.equals.get_right()[0]
    assert extended_brace.brace.get_left()[0] > equation.equals.get_right()[0]
    with pytest.raises(ValueError, match="range"):
        equation.rhs_brace("invalid", start=1, stop=1)
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
