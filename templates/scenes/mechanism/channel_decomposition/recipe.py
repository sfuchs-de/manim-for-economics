"""Atomic recipe for decomposing one outcome into economic channels."""

from pathlib import Path

from manim import Create, FadeIn

from econ_manim import ChannelDecomposition, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "channels.csv",
    required_columns=("order", "label", "color_role"),
)


def make_channel_decomposition(theme):
    ordered = sorted(ROWS, key=lambda row: int(row["order"]))
    return ChannelDecomposition(
        tuple((row["label"], getattr(theme, row["color_role"])) for row in ordered),
        outcome="change in welfare",
        theme=theme,
    )


def build_channel_decomposition(scene):
    decomposition = make_channel_decomposition(scene.theme)
    scene.play(FadeIn(decomposition.outcome), run_time=0.45)
    for channel, arrow in zip(
        decomposition.channels,
        decomposition.arrows,
        strict=True,
    ):
        scene.play(FadeIn(channel), Create(arrow), run_time=0.6)
    scene.wait(1.0)
    return decomposition


class ChannelDecompositionRecipe(ResearchScene):
    def construct(self):
        self.show_title("Reveal one economic channel at a time", run_time=0.45)
        self.set_caption(
            "Illustrative labels · distinguish conceptual channels from identified effects.",
            run_time=0.35,
        )
        build_channel_decomposition(self)
