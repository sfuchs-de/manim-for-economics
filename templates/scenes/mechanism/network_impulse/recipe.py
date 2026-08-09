"""Atomic recipe for recursive propagation of one local network impulse."""

from pathlib import Path

from manim import (
    DOWN,
    Circle,
    Create,
    Dot,
    FadeIn,
    Line,
    MathTex,
    ReplacementTransform,
    VGroup,
)

from econ_manim import ProseText, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "impulse.csv",
    required_columns=("round", "node", "value", "color_role"),
)
POSITIONS = {
    "A": (-4.3, 0.0, 0),
    "B": (-2.3, 0.0, 0),
    "C": (0.0, 0.0, 0),
    "D": (2.2, 1.15, 0),
    "E": (2.2, -1.15, 0),
    "F": (4.4, 0.0, 0),
}
EDGES = (("A", "B"), ("B", "C"), ("C", "D"), ("C", "E"), ("D", "F"), ("E", "F"))


def _network(theme):
    edges = VGroup(
        *[
            Line(POSITIONS[source], POSITIONS[target], color=theme.grid, stroke_width=2.2)
            for source, target in EDGES
        ]
    )
    nodes = VGroup()
    labels = VGroup()
    for name, position in POSITIONS.items():
        nodes.add(Dot(position, radius=0.12, color=theme.foreground))
        labels.add(
            ProseText(name, font_size=17, color=theme.muted).next_to(
                nodes[-1], DOWN, buff=0.10
            )
        )
    return VGroup(edges, nodes, labels)


def _round_halos(round_number, theme):
    halos = VGroup()
    for row in ROWS:
        if int(row["round"]) != round_number:
            continue
        color = getattr(theme, row["color_role"])
        radius = 0.22 + 0.12 * float(row["value"])
        halos.add(
            Circle(radius=radius, color=color, stroke_width=4.0).move_to(
                POSITIONS[row["node"]]
            )
        )
    return halos


def build_network_impulse(scene):
    network = _network(scene.theme)
    scene.play(FadeIn(network), run_time=0.55)

    equations = (
        MathTex(r"u=g", font_size=38, color=scene.theme.orange),
        MathTex(r"u=g+\Omega g", font_size=38, color=scene.theme.foreground),
        MathTex(
            r"u=g+\Omega g+\Omega^2g+\cdots",
            font_size=38,
            color=scene.theme.foreground,
        ),
        MathTex(
            r"u=(I-\Omega)^{-1}g",
            font_size=40,
            color=scene.theme.green,
        ),
    )
    for equation in equations:
        equation.move_to([0, -2.25, 0])

    direct = _round_halos(0, scene.theme)
    first = _round_halos(1, scene.theme)
    second = _round_halos(2, scene.theme)
    scene.play(Create(direct), FadeIn(equations[0]), run_time=0.60)
    scene.play(
        Create(first),
        ReplacementTransform(equations[0], equations[1]),
        run_time=0.70,
    )
    scene.play(
        Create(second),
        ReplacementTransform(equations[1], equations[2]),
        run_time=0.70,
    )
    scene.play(ReplacementTransform(equations[2], equations[3]), run_time=0.55)
    note = ProseText(
        "Each round applies the one-step response operator Ω.",
        font_size=19,
        color=scene.theme.muted,
    ).move_to([0, -2.85, 0])
    scene.play(FadeIn(note), run_time=0.35)
    scene.wait(0.90)
    return VGroup(network, direct, first, second, equations[3], note)


class NetworkImpulseRecipe(ResearchScene):
    def construct(self):
        self.show_title("Trace a local shock through recursive rounds", run_time=0.45)
        build_network_impulse(self)
