"""Atomic recipe for movement through economically meaningful paths."""

from pathlib import Path

from manim import Create, Dot, FadeIn, VGroup

from econ_manim import PathFlow, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "path_flow.csv",
    required_columns=("route", "order", "x", "y", "label", "color_role", "curved"),
)


def make_path_flows(theme):
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in ROWS:
        grouped.setdefault(row["route"], []).append(row)
    flows = VGroup()
    for rows in grouped.values():
        ordered = sorted(rows, key=lambda row: int(row["order"]))
        color = getattr(theme, ordered[0]["color_role"])
        flows.add(
            PathFlow(
                [(float(row["x"]), float(row["y"]), 0) for row in ordered],
                label=ordered[0]["label"],
                color=color,
                curved=ordered[0]["curved"].lower() == "true",
                theme=theme,
            )
        )
    return flows


def build_path_flow(scene):
    theme = scene.theme
    nodes = VGroup(
        Dot([-4.2, 0.5, 0], radius=0.14, color=theme.foreground),
        Dot([-1.5, 0.5, 0], radius=0.14, color=theme.foreground),
        Dot([-1.1, -0.7, 0], radius=0.14, color=theme.foreground),
        Dot([1.2, 0.1, 0], radius=0.14, color=theme.foreground),
        Dot([4.1, -0.5, 0], radius=0.14, color=theme.foreground),
    )
    flows = make_path_flows(theme)
    scene.play(FadeIn(nodes), run_time=0.45)
    for flow in flows:
        scene.play(Create(flow.path), FadeIn(flow.label), run_time=0.55)
        scene.play(flow.travel_animation(run_time=0.9))
    scene.wait(0.8)
    return VGroup(nodes, flows)


class PathFlowRecipe(ResearchScene):
    def construct(self):
        self.show_title("Trace adjustment through a stable system", run_time=0.45)
        self.set_caption(
            "Illustrative paths · replace labels and coordinates with the paper's mechanism.",
            run_time=0.35,
        )
        build_path_flow(self)
