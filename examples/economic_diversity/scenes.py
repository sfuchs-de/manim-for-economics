"""One final, readable case-study scene composed from seven chapter functions."""

from chapters import (
    conclusion,
    diversity,
    evidence,
    identification,
    opening,
    welfare,
    worker_adjustment,
)

from econ_manim import ResearchScene


class EconomicDiversityExplainer(ResearchScene):
    def construct(self):
        opening(self)
        worker_adjustment(self)
        diversity(self)
        identification(self)
        evidence(self)
        welfare(self)
        conclusion(self)
