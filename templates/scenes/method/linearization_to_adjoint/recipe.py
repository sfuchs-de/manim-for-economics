"""Staged derivation from an equilibrium system to one welfare adjoint."""

from pathlib import Path

from manim import DOWN, FadeIn, FadeOut, MathTex, Succession, VGroup

from econ_manim import ProseText, ResearchScene, fit_prose_text, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "workflow.csv",
    required_columns=("step", "label", "formula"),
)
EXPECTED_STEPS = (
    "Equilibrium system",
    "Linearization",
    "State response",
    "Welfare projection",
    "Adjoint system",
    "Policy value",
)
if tuple(row["label"] for row in ROWS) != EXPECTED_STEPS:
    raise ValueError("workflow.csv must preserve the six-stage adjoint derivation")


def _equation(formula, *, color, font_size=38):
    return MathTex(formula, font_size=font_size, color=color)


def build_linearization_to_adjoint(scene):
    equilibrium = _equation(r"G(z,\theta)=0", color=scene.theme.foreground, font_size=44)
    equilibrium.move_to([0, 0.45, 0])
    interpretation = ProseText(
        "States adjust until every equilibrium condition is satisfied.",
        font_size=20,
        color=scene.theme.muted,
    ).next_to(equilibrium, DOWN, buff=0.42)
    scene.play(FadeIn(equilibrium), FadeIn(interpretation), run_time=0.65)
    scene.wait(0.55)

    linearized = _equation(
        r"J\,dz+b_e\,d\theta_e=0",
        color=scene.theme.foreground,
        font_size=42,
    ).move_to(equilibrium)
    local_note = fit_prose_text(
        "Differentiate once. J maps state changes into residuals; b_e is the local shock.",
        max_width=9.6,
        font_size=20,
        min_font_size=17,
        color=scene.theme.muted,
    ).move_to(interpretation)
    scene.play(
        Succession(FadeOut(equilibrium), FadeIn(linearized)),
        Succession(FadeOut(interpretation), FadeIn(local_note)),
        run_time=0.85,
    )
    equilibrium = linearized
    interpretation = local_note
    scene.wait(0.70)

    state_response = _equation(
        r"\frac{dz}{d\theta_e}=-J^{-1}b_e",
        color=scene.theme.blue,
        font_size=42,
    ).move_to(equilibrium)
    repeated = ProseText(
        "Direct evaluation repeats this high-dimensional state calculation for every policy.",
        font_size=20,
        color=scene.theme.muted,
    ).move_to(interpretation)
    scene.play(
        Succession(FadeOut(equilibrium), FadeIn(state_response)),
        Succession(FadeOut(interpretation), FadeIn(repeated)),
        run_time=0.85,
    )
    equilibrium = state_response
    interpretation = repeated
    scene.wait(0.75)

    projection = VGroup(
        _equation(r"d\ln W=q^\top dz", color=scene.theme.orange, font_size=38),
        _equation(r"\Longrightarrow", color=scene.theme.muted, font_size=35),
        _equation(
            r"\frac{d\ln W}{d\theta_e}=-q^\top J^{-1}b_e",
            color=scene.theme.foreground,
            font_size=38,
        ),
    ).arrange(direction=[1, 0, 0], buff=0.28)
    projection.move_to(equilibrium)
    welfare_note = ProseText(
        "Welfare needs only one projection of the full state response.",
        font_size=20,
        color=scene.theme.muted,
    ).move_to(interpretation)
    scene.play(
        Succession(FadeOut(equilibrium), FadeIn(projection)),
        Succession(FadeOut(interpretation), FadeIn(welfare_note)),
        run_time=0.85,
    )
    current_equation = projection
    interpretation = welfare_note
    scene.wait(0.75)

    adjoint = VGroup(
        _equation(r"J^\top\ell=q", color=scene.theme.green, font_size=42),
        _equation(r"\Longrightarrow", color=scene.theme.muted, font_size=35),
        _equation(
            r"\frac{d\ln W}{d\theta_e}=-\ell^\top b_e",
            color=scene.theme.foreground,
            font_size=40,
        ),
    ).arrange(direction=[1, 0, 0], buff=0.34)
    adjoint.move_to(current_equation)
    adjoint_note = fit_prose_text(
        "Solve one transposed system for the welfare weights.\n"
        "Each policy then needs only a sparse inner product.",
        max_width=10.2,
        font_size=20,
        min_font_size=17,
        color=scene.theme.muted,
    ).move_to(interpretation)
    scene.play(
        Succession(FadeOut(current_equation), FadeIn(adjoint)),
        Succession(FadeOut(interpretation), FadeIn(adjoint_note)),
        run_time=0.95,
    )
    interpretation = adjoint_note
    scene.wait(1.15)
    return VGroup(adjoint, interpretation)


class LinearizationToAdjointRecipe(ResearchScene):
    def construct(self):
        self.show_title("From equilibrium differentiation to one welfare adjoint", run_time=0.45)
        build_linearization_to_adjoint(self)
