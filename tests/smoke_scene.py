from manim import FadeIn, MathTex, Text, VGroup

from econ_manim import ECON_DARK, ResearchScene


class SmokeScene(ResearchScene):
    def construct(self):
        self.show_title("Smoke render")
        group = VGroup(
            Text("worker welfare", font_size=28, color=ECON_DARK.foreground),
            MathTex(r"=", font_size=34, color=ECON_DARK.muted),
            Text("first order", font_size=28, color=ECON_DARK.blue),
        ).arrange()
        self.play(FadeIn(group), run_time=0.5)
        self.wait(0.5)
