"""Paper-independent skeleton for an agent-choice-welfare explainer."""

from manim import UP, Arrow, Circle, Create, FadeIn, FadeOut, Indicate, Text, VGroup

from econ_manim import (
    ECON_DARK,
    ChoiceMap,
    EquationBuild,
    ImpulseResponsePlot,
    ResearchScene,
)


def example_menu():
    return ChoiceMap(
        (
            ("current action", ECON_DARK.blue),
            ("alternative", ECON_DARK.green),
            ("wait or exit", ECON_DARK.orange),
        ),
        agent_label="decision maker",
    )


class ChoiceWelfareExplainer(ResearchScene):
    def construct(self):
        self.next_section("agent")
        self.show_title("Begin with a decision, not a formula")
        self.set_caption("The token can represent any economic decision maker.")
        menu = example_menu().scale(1.08).move_to([0, 0.05, 0])
        self.play(FadeIn(menu.origin), run_time=0.5)
        for route, row in zip(menu.routes, menu[2], strict=True):
            self.play(Create(route), FadeIn(row), run_time=0.35)
        self.wait(1.8)

        self.next_section("change")
        self.show_title("Change the menu or its payoffs")
        self.set_caption("Keep the origin fixed so the counterfactual remains easy to read.")
        change = Text("economic change", font_size=22, color=ECON_DARK.orange)
        change.move_to(menu.origin.get_center() + UP * 1.50)
        pointer = Arrow(
            change.get_bottom(),
            menu.origin.get_top(),
            buff=0.10,
            color=ECON_DARK.orange,
            stroke_width=2.2,
            tip_length=0.13,
        )
        halo = Circle(
            radius=0.36,
            stroke_color=ECON_DARK.orange,
            stroke_width=2.5,
        ).move_to(menu.origin.symbol)
        self.play(FadeIn(change), Create(pointer), Create(halo), run_time=0.8)
        self.play(Indicate(menu.nodes[1], color=ECON_DARK.green), run_time=0.7)
        self.wait(1.7)
        self.play(FadeOut(VGroup(menu, change, pointer, halo)), run_time=0.4)

        self.next_section("evidence")
        self.show_title("Estimate the same response margins")
        self.set_caption("Illustrative paths only · replace them and document the source.")
        responses = ImpulseResponsePlot(
            {
                "more options": ([0.00, 0.15, 0.22, 0.25], ECON_DARK.green),
                "fewer options": ([0.00, 0.07, 0.10, 0.12], ECON_DARK.orange),
            },
            title="response after the change",
            x_label="time after change",
        ).scale(1.15).move_to([0, -0.15, 0])
        self.play(FadeIn(responses), run_time=0.8)
        self.wait(2.2)
        self.clear_stage(responses, run_time=0.35)

        self.next_section("welfare")
        self.show_title("Connect choices to welfare")
        self.set_caption("Reveal each term with the matching choice margin.")
        small_menu = example_menu().scale(0.82).move_to([0, 1.15, 0])
        equation = EquationBuild(
            (
                ("direct payoff", ECON_DARK.blue),
                ("value of available responses", ECON_DARK.green),
            ),
            lhs="agent welfare",
        ).scale(0.92).move_to([0, -1.20, 0])
        self.play(FadeIn(small_menu), run_time=0.7)
        self.play(FadeIn(VGroup(equation.lhs, equation.equals)), run_time=0.5)
        self.play(
            FadeIn(equation.terms[0]),
            Indicate(small_menu.nodes[0], color=ECON_DARK.blue),
            run_time=0.7,
        )
        self.wait(0.7)
        self.play(
            FadeIn(equation.operators),
            FadeIn(equation.terms[1]),
            Indicate(VGroup(*small_menu.nodes[1:]), color=ECON_DARK.green),
            run_time=0.8,
        )
        self.wait(1.8)
        self.clear_stage(small_menu, equation, run_time=0.35)

        self.next_section("conclusion")
        self.show_title("Close on the supported interpretation")
        self.set_caption("State for whom, relative to what, and over what horizon.")
        takeaway = Text(
            "Choices shape both adjustment and value.",
            font_size=34,
            color=ECON_DARK.foreground,
        ).move_to([0, 0.25, 0])
        self.play(FadeIn(takeaway, shift=UP * 0.08), run_time=0.7)
        self.wait(2.0)
