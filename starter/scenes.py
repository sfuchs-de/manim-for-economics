"""A deliberately small scene to replace after the storyboard is approved."""

from manim import UP, FadeIn, FadeOut, Text, VGroup

from econ_manim import (
    ECON_DARK,
    CityLaborMarket,
    EquationBuild,
    ResearchScene,
    ShockDistribution,
)


class PaperExplainer(ResearchScene):
    def construct(self):
        self.next_section("question")
        self.show_title("What should the viewer learn?")
        self.set_caption("Begin with one economic question, not a list of paper sections.")
        question = Text(
            "Replace this with your paper's central question.",
            font_size=34,
            color=ECON_DARK.foreground,
        ).move_to([0, 0.45, 0])
        self.play(FadeIn(question, shift=UP * 0.10), run_time=0.8)
        self.wait(2.0)

        self.next_section("agent")
        self.show_title("Situate the economic agent")
        self.set_caption("Use one recurring object so choices and shocks remain concrete.")
        city = CityLaborMarket("example city", (2, 2, 2, 2)).move_to([0, -0.15, 0])
        self.play(FadeOut(question), FadeIn(city), run_time=0.8)
        self.wait(2.2)

        self.next_section("evidence")
        self.show_title("Show one empirical object")
        self.set_caption("These dots are illustrative. Replace them and update the data manifest.")
        distribution = ShockDistribution(
            [
                (-0.8, ECON_DARK.orange),
                (-0.2, ECON_DARK.orange),
                (0.3, ECON_DARK.green),
                (0.7, ECON_DARK.green),
            ]
        ).move_to([0, -0.25, 0])
        self.play(FadeOut(city), FadeIn(distribution), run_time=0.8)
        self.wait(2.2)

        self.next_section("interpretation")
        self.show_title("Build the interpretation")
        self.set_caption("Introduce terms in words before replacing any of them with notation.")
        equation = EquationBuild(
            [
                ("first-order effect", ECON_DARK.blue),
                ("second-order correction", ECON_DARK.orange),
            ]
        ).move_to([0, 0.10, 0])
        equation.terms.set_opacity(0)
        equation.operators.set_opacity(0)
        self.play(FadeOut(distribution), FadeIn(VGroup(equation.lhs, equation.equals)), run_time=0.7)
        self.play(FadeIn(equation.terms[0]), run_time=0.6)
        self.wait(1.0)
        self.play(FadeIn(equation.operators), FadeIn(equation.terms[1]), run_time=0.6)
        self.wait(2.0)
