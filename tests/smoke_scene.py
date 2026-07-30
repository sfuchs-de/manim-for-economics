from manim import DOWN, FadeIn, MathTex, Text, VGroup

from econ_manim import ResearchScene, ShockDistribution


class SmokeScene(ResearchScene):
    def construct(self):
        theme = self.theme
        self.show_title("Smoke render")
        group = VGroup(
            Text("research outcome", font_size=28, color=theme.foreground),
            MathTex(r"=", font_size=34, color=theme.muted),
            Text("direct channel", font_size=28, color=theme.blue),
        ).arrange()
        shocks = ShockDistribution(
            [(-0.2, theme.orange), (0.3, theme.green)],
            width=3.5,
            theme=theme,
        ).scale(0.65).next_to(group, direction=DOWN, buff=0.45)
        self.play(FadeIn(group), FadeIn(shocks), run_time=0.5)
        self.wait(0.5)
