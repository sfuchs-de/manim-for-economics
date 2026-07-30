"""Reusable building blocks for economics paper explainers."""

from .charts import EquationBuild, ImpulseResponsePlot, ResultTable, ShockDistribution
from .components import CityLaborMarket, WorkerToken, adjustment_route
from .layout import LayoutError, assert_no_overlap, assert_within_frame
from .scene import ResearchScene
from .theme import ECON_DARK, VideoTheme

__all__ = [
    "ECON_DARK",
    "CityLaborMarket",
    "EquationBuild",
    "ImpulseResponsePlot",
    "LayoutError",
    "ResearchScene",
    "ResultTable",
    "ShockDistribution",
    "VideoTheme",
    "WorkerToken",
    "adjustment_route",
    "assert_no_overlap",
    "assert_within_frame",
]

__version__ = "0.1.0"
