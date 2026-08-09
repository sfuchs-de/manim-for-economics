"""Atomic recipe comparing repeated state solves with one welfare adjoint."""

from pathlib import Path

from manim import DOWN, Arrow, FadeIn, FadeOut, MathTex, RoundedRectangle, VGroup

from econ_manim import ProseText, ResearchScene, fit_prose_text, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "workflow.csv",
    required_columns=("order", "label", "color_role"),
)


def _card(title, formula, color, theme, *, width=3.05):
    heading = fit_prose_text(
        title,
        max_width=width - 0.35,
        font_size=20,
        min_font_size=15,
        color=color,
        weight="BOLD",
    )
    equation = MathTex(formula, font_size=31, color=theme.foreground)
    content = VGroup(heading, equation).arrange(DOWN, buff=0.24)
    box = RoundedRectangle(
        width=width,
        height=1.45,
        corner_radius=0.10,
        stroke_color=color,
        stroke_width=1.6,
        fill_color=theme.card,
        fill_opacity=0.94,
    )
    content.move_to(box)
    return VGroup(box, content)


def build_adjoint_sweep(scene):
    ordered = sorted(ROWS, key=lambda row: int(row["order"]))
    colors = {row["label"]: getattr(scene.theme, row["color_role"]) for row in ordered}

    policies = _card(
        "K policy shocks",
        r"B=[b_1\;\cdots\;b_K]",
        colors["policy forcing vectors"],
        scene.theme,
    ).move_to([-4.45, 0.15, 0])
    direct = _card(
        "K state solves",
        r"J\,dz_e=-b_e",
        colors["equilibrium Jacobian"],
        scene.theme,
    ).move_to([0, 0.15, 0])
    outcomes = _card(
        "K welfare derivatives",
        r"q^\top dz_e",
        colors["policy derivatives"],
        scene.theme,
    ).move_to([4.45, 0.15, 0])
    arrows = VGroup(
        Arrow(policies.get_right(), direct.get_left(), buff=0.16, color=scene.theme.muted),
        Arrow(direct.get_right(), outcomes.get_left(), buff=0.16, color=scene.theme.muted),
    )
    scene.play(FadeIn(policies), FadeIn(direct), FadeIn(outcomes), FadeIn(arrows), run_time=0.75)

    direct_note = ProseText(
        "Direct method: solve for the state response to every shock.",
        font_size=19,
        color=scene.theme.muted,
    ).move_to([0, -1.45, 0])
    scene.play(FadeIn(direct_note), run_time=0.35)
    scene.wait(0.45)

    adjoint = _card(
        "One adjoint solve",
        r"J^\top\ell=q",
        colors["welfare gradient"],
        scene.theme,
    ).move_to([0, 0.15, 0])
    inner_products = _card(
        "K sparse inner products",
        r"-\ell^\top b_e",
        colors["policy derivatives"],
        scene.theme,
    ).move_to([4.45, 0.15, 0])
    adjoint_arrows = VGroup(
        Arrow(policies.get_right(), adjoint.get_left(), buff=0.16, color=scene.theme.muted),
        Arrow(adjoint.get_right(), inner_products.get_left(), buff=0.16, color=scene.theme.muted),
    )
    scene.play(
        FadeOut(direct),
        FadeOut(outcomes),
        FadeOut(arrows),
        FadeOut(direct_note),
        FadeIn(adjoint),
        FadeIn(inner_products),
        FadeIn(adjoint_arrows),
        run_time=0.80,
    )
    condition = ProseText(
        "Same Jacobian · most useful when outcomes are few and policy shocks are many",
        font_size=19,
        color=scene.theme.muted,
    ).move_to([0, -1.45, 0])
    scene.play(FadeIn(condition), run_time=0.40)
    scene.wait(1.10)
    return VGroup(policies, adjoint, inner_products, adjoint_arrows, condition)


class AdjointSweepRecipe(ResearchScene):
    def construct(self):
        self.show_title("Evaluate many policy shocks with one welfare adjoint", run_time=0.45)
        build_adjoint_sweep(self)
