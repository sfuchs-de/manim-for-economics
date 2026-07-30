"""Narrative chapters for the economic-diversity case study."""

from __future__ import annotations

from data import (
    SPATIAL_NEG_CONCENTRATED,
    SPATIAL_NEG_DIVERSE,
    WITHIN_NEG_CONCENTRATED,
    WITHIN_NEG_DIVERSE,
    released_shocks,
    welfare_rows,
)
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    CurvedArrow,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    MathTex,
    Text,
    VGroup,
)

from econ_manim import (
    CityLaborMarket,
    EquationBuild,
    ImpulseResponsePlot,
    ResultTable,
    ShockDistribution,
    WorkerToken,
    adjustment_route,
)


def _city_pair(theme):
    diverse = CityLaborMarket(
        "diversified city",
        (2, 2, 2, 2),
        accent=theme.green,
        theme=theme,
    ).move_to([-3.25, -0.15, 0])
    concentrated = CityLaborMarket(
        "concentrated city",
        (5, 1, 1, 1),
        accent=theme.orange,
        theme=theme,
    ).move_to([3.25, -0.15, 0])
    return diverse, concentrated


def opening(scene):
    theme = scene.theme
    scene.next_section("opening")
    scene.show_title("Which city better protects workers?")
    scene.set_caption(
        "Two cities have the same number of workers, but different sector–occupation mixes."
    )
    diverse, concentrated = _city_pair(theme)
    same_size = Text(
        "same employment · different composition",
        font_size=21,
        color=theme.muted,
    ).move_to([0, -2.25, 0])
    scene.play(
        FadeIn(diverse, shift=UP * 0.08),
        FadeIn(concentrated, shift=UP * 0.08),
        FadeIn(same_size),
        run_time=1.0,
    )
    scene.wait(1.2)
    shocks = VGroup(diverse.shock_cell(0), concentrated.shock_cell(0))
    scene.set_caption("Now expose the same sector–occupation cell to an adverse shock.")
    scene.play(FadeIn(shocks), run_time=0.6)
    scene.play(Indicate(shocks, color=theme.orange), run_time=0.8)
    scene.wait(1.5)
    scene.clear_stage(diverse, concentrated, same_size, shocks)


def worker_adjustment(scene):
    theme = scene.theme
    scene.next_section("worker-adjustment")
    scene.show_title("A worker can adjust along three margins")
    scene.set_caption(
        "Workers occupy sector–occupation–city labor markets; the shock changes their menu."
    )
    city_a = CityLaborMarket(
        "city A",
        (2, 2, 2, 2),
        radius=1.30,
        theme=theme,
    ).move_to([-3.55, -0.05, 0])
    city_b = CityLaborMarket(
        "city B",
        (2, 2, 2, 2),
        radius=1.30,
        accent=theme.blue,
        theme=theme,
    ).move_to([3.55, -0.05, 0])
    worker = WorkerToken(color=theme.foreground, scale=0.72, theme=theme).move_to(
        city_a.cells[0].get_center()
    )
    exit_node = Circle(
        radius=0.23,
        color=theme.muted,
        stroke_width=1.6,
    ).move_to([-0.35, -2.10, 0])
    scene.play(FadeIn(city_a), FadeIn(city_b), FadeIn(worker), run_time=0.9)

    local = adjustment_route(
        worker.get_center(),
        city_a.cells[3].get_center(),
        label="switch locally",
        color=theme.green,
        curved=True,
        label_direction=LEFT,
    )
    move = adjustment_route(
        worker.get_center(),
        city_b.cells[1].get_center(),
        label="move to another city",
        color=theme.blue,
        curved=True,
        label_direction=UP,
    )
    leave = adjustment_route(
        worker.get_center(),
        exit_node.get_center(),
        label="leave employment",
        color=theme.orange,
        label_direction=DOWN,
    )
    local[1].move_to([-5.55, 0.62, 0])
    move[1].move_to([0.10, 0.86, 0])
    leave[1].move_to([-1.85, -2.35, 0])
    routes = (local, move, leave)
    captions = (
        "Local switching keeps the worker in the same city.",
        "Spatial mobility reaches a different local labor market.",
        "Non-employment is the third adjustment margin.",
    )
    for route, caption in zip(routes, captions, strict=True):
        scene.set_caption(caption)
        scene.play(Create(route[0]), FadeIn(route[1]), run_time=0.7)
        scene.wait(0.8)
    scene.play(FadeIn(exit_node), run_time=0.35)
    scene.wait(1.3)
    scene.clear_stage(city_a, city_b, worker, exit_node, *routes)


def diversity(scene):
    theme = scene.theme
    scene.next_section("diversity")
    scene.show_title("Diversity expands the local menu")
    scene.set_caption("HHI summarizes how concentrated employment is across local labor markets.")
    diverse, concentrated = _city_pair(theme)
    explanations = VGroup(
        Text("lower HHI", font_size=24, color=theme.green).move_to([-3.25, 1.95, 0]),
        Text("higher HHI", font_size=24, color=theme.orange).move_to([3.25, 1.95, 0]),
    )
    hhi_words = VGroup(
        MathTex(r"\mathrm{HHI}", font_size=40, color=theme.foreground),
        Text(
            "concentration of employment across sector–occupation cells",
            font_size=23,
            color=theme.muted,
        ),
    ).arrange(RIGHT, buff=0.28).move_to([0, 2.48, 0])
    if hhi_words.width > 11.8:
        hhi_words.scale_to_fit_width(11.8)
    scene.play(FadeIn(hhi_words), FadeIn(diverse), FadeIn(concentrated), FadeIn(explanations))

    diverse_shock = diverse.shock_cell(0)
    concentrated_shock = concentrated.shock_cell(0)
    scene.play(FadeIn(diverse_shock), FadeIn(concentrated_shock), run_time=0.5)
    diverse_paths = VGroup(
        CurvedArrow(
            diverse.cells[0].get_center(),
            diverse.cells[index].get_center(),
            angle=(-0.28 if index % 2 else 0.28),
            color=theme.green,
            stroke_width=2.2,
            tip_length=0.12,
        )
        for index in (1, 2, 3)
    )
    concentrated_path = CurvedArrow(
        concentrated.cells[0].get_center(),
        concentrated.cells[1].get_center(),
        angle=-0.28,
        color=theme.orange,
        stroke_width=2.2,
        tip_length=0.12,
    )
    scene.set_caption("After the same shock, the diversified city offers more nearby alternatives.")
    scene.play(
        *[Create(path) for path in diverse_paths],
        Create(concentrated_path),
        run_time=1.0,
    )
    scene.wait(2.2)
    scene.clear_stage(
        diverse,
        concentrated,
        explanations,
        hhi_words,
        diverse_shock,
        concentrated_shock,
        diverse_paths,
        concentrated_path,
    )


def identification(scene):
    theme = scene.theme
    scene.next_section("identification")
    scene.show_title("The empirical shock varies across cities and years")
    scene.set_caption(
        "These are released city-year observations, not invented national-growth bars."
    )
    colors = {2005: theme.blue, 2009: theme.orange, 2019: theme.green}
    observations = [
        (float(row["bartik"]), colors[int(row["year"])])
        for row in released_shocks()
    ]
    distribution = ShockDistribution(
        observations,
        x_range=(-0.5, 1.3, 0.25),
        label="released Bartik shock · selected major commuting zones",
        theme=theme,
    ).move_to([0, 0.35, 0])
    year_key = VGroup(
        *[
            VGroup(
                Circle(radius=0.06, color=color, fill_color=color, fill_opacity=1),
                Text(str(year), font_size=18, color=color),
            ).arrange(RIGHT, buff=0.10)
            for year, color in colors.items()
        ]
    ).arrange(RIGHT, buff=0.45).move_to([0, -1.55, 0])
    source = Text(
        "source: public replication package · selected cities",
        font_size=17,
        color=theme.muted,
    ).move_to([0, -2.20, 0])
    scene.play(FadeIn(distribution), FadeIn(year_key), FadeIn(source), run_time=0.9)
    scene.wait(1.8)

    formula = VGroup(
        Text("predetermined local exposure", font_size=23, color=theme.blue),
        MathTex(r"\times", font_size=34, color=theme.muted),
        Text("national sector growth", font_size=23, color=theme.green),
        Arrow(ORIGIN, RIGHT * 0.8, color=theme.muted, stroke_width=2.2),
        Text("local labor-demand shock", font_size=23, color=theme.orange),
    ).arrange(RIGHT, buff=0.22)
    if formula.width > 12.4:
        formula.scale_to_fit_width(12.4)
    formula.move_to([0, 0.45, 0])
    lpiv = Text(
        "LPIV traces how worker flows respond over the next 20 quarters",
        font_size=24,
        color=theme.foreground,
    ).move_to([0, -0.75, 0])
    scene.set_caption("Predetermined exposure turns common national growth into local variation.")
    scene.play(
        FadeOut(distribution),
        FadeOut(year_key),
        FadeOut(source),
        FadeIn(formula),
        run_time=0.8,
    )
    scene.play(FadeIn(lpiv, shift=UP * 0.08), run_time=0.6)
    scene.wait(2.0)
    scene.clear_stage(formula, lpiv)


def evidence(scene):
    theme = scene.theme
    scene.next_section("evidence")
    scene.show_title("Adjustment differs most after adverse shocks")
    scene.set_caption(
        "Published Figure 3 point estimates: higher-HHI cities show larger declines."
    )
    within = ImpulseResponsePlot(
        {
            "lower HHI": (WITHIN_NEG_DIVERSE, theme.green),
            "higher HHI": (WITHIN_NEG_CONCENTRATED, theme.orange),
        },
        title="within-city job changes",
        y_range=(-1.1, 0.2, 0.25),
        width=5.1,
        height=2.65,
        theme=theme,
    ).move_to([-3.25, -0.10, 0])
    spatial = ImpulseResponsePlot(
        {
            "lower HHI": (SPATIAL_NEG_DIVERSE, theme.green),
            "higher HHI": (SPATIAL_NEG_CONCENTRATED, theme.orange),
        },
        title="moves across cities",
        y_range=(-1.8, 0.3, 0.5),
        width=5.1,
        height=2.65,
        theme=theme,
    ).move_to([3.25, -0.10, 0])
    note = Text(
        "central estimates digitized from Figure 3 · confidence bands omitted here",
        font_size=17,
        color=theme.muted,
    ).move_to([0, -2.35, 0])
    scene.play(FadeIn(within.axes), FadeIn(spatial.axes), run_time=0.5)
    scene.play(
        *[Create(line) for line in within.lines],
        *[Create(line) for line in spatial.lines],
        FadeIn(within.labels),
        FadeIn(spatial.labels),
        FadeIn(within[4]),
        FadeIn(within[5]),
        FadeIn(spatial[4]),
        FadeIn(spatial[5]),
        FadeIn(note),
        run_time=1.1,
    )
    scene.wait(2.6)
    scene.set_caption("Diversity matters mainly by protecting the downside.")
    scene.play(
        Indicate(within.lines[0], color=theme.green),
        Indicate(spatial.lines[0], color=theme.green),
        run_time=0.8,
    )
    scene.wait(1.5)
    scene.clear_stage(within, spatial, note)


def _welfare_network(theme):
    origin = WorkerToken(
        color=theme.foreground,
        scale=0.72,
        theme=theme,
    ).move_to([-4.85, -0.15, 0])
    nodes = VGroup(
        Text("stay", font_size=19, color=theme.foreground).move_to([-2.50, 1.00, 0]),
        Text("switch locally", font_size=19, color=theme.green).move_to(
            [-2.28, -0.10, 0]
        ),
        Text("move", font_size=19, color=theme.blue).move_to([-2.48, -1.20, 0]),
    )
    arrows = VGroup(
        Arrow(
            origin.get_right(),
            node.get_left(),
            buff=0.10,
            color=color,
            stroke_width=2.2,
            tip_length=0.13,
        )
        for node, color in zip(
            nodes,
            (theme.foreground, theme.green, theme.blue),
            strict=True,
        )
    )
    return VGroup(origin, nodes, arrows), nodes, arrows


def welfare(scene):
    theme = scene.theme
    scene.next_section("welfare")
    scene.show_title("From worker flows to welfare")
    scene.set_caption(
        "First order weights changes in staying, switching locally, and moving."
    )
    equation = EquationBuild(
        [
            ("first-order response", theme.blue),
            ("second-order insurance", theme.green),
        ],
        lhs="worker welfare",
        theme=theme,
    ).move_to([0, 2.20, 0])
    network, nodes, arrows = _welfare_network(theme)
    first_note = VGroup(
        Text("LPIV flow responses", font_size=23, color=theme.blue),
        MathTex(r"\times", font_size=30, color=theme.muted),
        Text("baseline welfare weights", font_size=23, color=theme.foreground),
    ).arrange(RIGHT, buff=0.18).move_to([2.55, 0.55, 0])
    second_note = Text(
        "curvature + co-movement, scaled by worker responsiveness",
        font_size=20,
        color=theme.green,
    ).move_to([2.55, -0.60, 0])
    scene.play(FadeIn(VGroup(equation.lhs, equation.equals)), FadeIn(network), run_time=0.8)
    scene.play(
        FadeIn(equation.terms[0]),
        *[GrowArrow(arrow) for arrow in arrows],
        FadeIn(first_note),
        run_time=0.9,
    )
    scene.wait(1.3)

    interactions = VGroup(
        CurvedArrow(
            nodes[0].get_right(),
            nodes[1].get_right(),
            angle=-0.55,
            color=theme.green,
            stroke_width=1.6,
            tip_length=0.10,
        ),
        CurvedArrow(
            nodes[1].get_right(),
            nodes[2].get_right(),
            angle=-0.55,
            color=theme.green,
            stroke_width=1.6,
            tip_length=0.10,
        ),
    )
    scene.set_caption(
        "Second order captures curvature and co-movement across those same margins."
    )
    scene.play(
        FadeIn(equation.operators),
        FadeIn(equation.terms[1]),
        Create(interactions),
        FadeIn(second_note),
        run_time=0.9,
    )
    scene.wait(1.7)
    scene.clear_stage(
        equation,
        network,
        first_note,
        second_note,
        interactions,
        run_time=0.30,
    )

    scene.show_title(
        "Average welfare effects for workers in France",
        run_time=0.40,
    )
    scene.set_caption(
        "Realized French shocks are averaged by HHI bin and evaluated relative to baseline.",
        run_time=0.25,
    )
    headers = (
        ("direct effect", theme.blue),
        ("second order", theme.green),
        ("total", theme.foreground),
    )
    negative = ResultTable(
        headers,
        welfare_rows(theme, "negative"),
        theme=theme,
    ).move_to([0, 0.35, 0])
    detail = Text(
        "discounted cumulative change · 2006Q1–2019Q4 · beta=.99 · horizons 0–20 · Table 2",
        font_size=17,
        color=theme.muted,
    ).move_to([0, -2.10, 0])
    sign_label = Text("negative realizations", font_size=25, color=theme.orange).move_to(
        [0, 2.20, 0]
    )
    scene.play(FadeIn(sign_label), FadeIn(negative), FadeIn(detail), run_time=0.70)
    scene.wait(2.6)

    positive = ResultTable(
        headers,
        welfare_rows(theme, "positive"),
        theme=theme,
    ).move_to(negative)
    positive_label = Text("positive realizations", font_size=25, color=theme.green).move_to(
        sign_label
    )
    scene.set_caption(
        "Positive realizations produce gains, but second order offsets part of the upside."
    )
    scene.play(
        FadeOut(negative),
        FadeIn(positive),
        FadeOut(sign_label),
        FadeIn(positive_label),
        run_time=0.8,
    )
    scene.wait(2.5)
    scene.clear_stage(positive, positive_label, detail)


def conclusion(scene):
    theme = scene.theme
    scene.next_section("conclusion")
    scene.show_title("Economic diversity is urban insurance")
    scene.set_caption("Diversity protects the downside by expanding workers' local options.")
    steps = VGroup(
        Text("lower sector–occupation HHI", font_size=30, color=theme.green),
        Text("more local adjustment options", font_size=30, color=theme.blue),
        Text("smaller flow contraction after adverse shocks", font_size=30, color=theme.orange),
        Text("smaller total welfare loss", font_size=32, color=theme.foreground),
    ).arrange(DOWN, buff=0.55)
    arrows = VGroup()
    for upper, lower in zip(steps[:-1], steps[1:], strict=True):
        arrows.add(
            Arrow(
                upper.get_bottom(),
                lower.get_top(),
                buff=0.10,
                color=theme.grid,
                stroke_width=1.8,
                tip_length=0.12,
            )
        )
    VGroup(steps, arrows).move_to([0, 0.10, 0])
    citation = Text(
        "de Soyres · Fuchs · Kondo · Maghin · Journal of International Economics (2025)",
        font_size=18,
        color=theme.muted,
    ).move_to([0, -2.50, 0])
    for step, arrow in zip(steps, list(arrows) + [None], strict=True):
        scene.play(FadeIn(step, shift=UP * 0.06), run_time=0.45)
        if arrow is not None:
            scene.play(GrowArrow(arrow), run_time=0.30)
    scene.play(FadeIn(citation), run_time=0.5)
    scene.wait(3.0)
