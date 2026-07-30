"""A domain-neutral scene to replace after the storyboard is approved."""

from manim import UP, FadeIn, Text, VGroup

from econ_manim import (
    CausalChain,
    DivergingBarChart,
    EquationBuild,
    ResearchScene,
)


class PaperExplainer(ResearchScene):
    def construct(self):
        theme = self.theme
        self.next_section("question")
        self.show_title("What should the viewer learn?")
        self.set_caption("Begin with one research question, not a list of paper sections.")
        question = Text(
            "Replace this with your paper's central question.",
            font_size=34,
            color=theme.foreground,
        ).move_to([0, 0.45, 0])
        self.play(FadeIn(question, shift=UP * 0.10), run_time=0.8)
        self.wait(2.0)
        self.clear_stage(question, run_time=0.35)

        self.next_section("argument")
        self.show_title("Build one persistent argument")
        self.set_caption("Name the objects in words before introducing notation.")
        chain = CausalChain(
            (
                ("research object", theme.blue),
                ("change or comparison", theme.orange),
                ("mechanism", theme.green),
                ("result", theme.foreground),
            ),
            theme=theme,
        ).scale(1.12).move_to([0, 0.20, 0])
        self.play(FadeIn(chain, shift=UP * 0.08), run_time=0.8)
        self.wait(2.2)
        self.clear_stage(chain, run_time=0.35)

        self.next_section("result")
        self.show_title("Show the result in its native form")
        self.set_caption("Illustrative values only · replace them and update the data manifest.")
        result = DivergingBarChart(
            (
                ("scenario A", 35, theme.green),
                ("scenario B", -20, theme.orange),
            ),
            benchmark_label="reference case",
            left_label="lower",
            right_label="higher",
            theme=theme,
        ).scale(1.20).move_to([0, -0.15, 0])
        self.play(FadeIn(result), run_time=0.8)
        self.wait(2.2)
        self.clear_stage(result, run_time=0.35)

        self.next_section("interpretation")
        self.show_title("Build the interpretation")
        self.set_caption("Add each term only when the matching idea is active on screen.")
        equation = EquationBuild(
            (
                ("main channel", theme.blue),
                ("interaction or correction", theme.orange),
            ),
            lhs="outcome",
            theme=theme,
        ).scale(1.06).move_to([0, 0.10, 0])
        self.play(FadeIn(VGroup(equation.lhs, equation.equals)), run_time=0.7)
        self.play(FadeIn(equation.terms[0]), run_time=0.6)
        self.wait(0.9)
        self.play(FadeIn(equation.operators), FadeIn(equation.terms[1]), run_time=0.6)
        self.wait(2.0)
