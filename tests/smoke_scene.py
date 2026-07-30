from manim import DOWN, FadeIn, MathTex, Text, VGroup

from econ_manim import ECON_DARK, ResearchScene, ShockDistribution


class SmokeScene(ResearchScene):
    def construct(self):
        self.show_title("Smoke render")
        group = VGroup(
            Text("research outcome", font_size=28, color=ECON_DARK.foreground),
            MathTex(r"=", font_size=34, color=ECON_DARK.muted),
            Text("direct channel", font_size=28, color=ECON_DARK.blue),
        ).arrange()
        shocks = ShockDistribution(
            [(-0.2, ECON_DARK.orange), (0.3, ECON_DARK.green)],
            width=3.5,
        ).scale(0.65).next_to(group, direction=DOWN, buff=0.45)
        self.play(FadeIn(group), FadeIn(shocks), run_time=0.5)
        self.wait(0.5)
