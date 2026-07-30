"""Reusable building blocks for economics paper explainers."""

from .charts import EquationBuild, ImpulseResponsePlot, ResultTable, ShockDistribution
from .components import AgentToken, ChoiceMap, CityLaborMarket, WorkerToken, adjustment_route
from .formats import CausalChain, DivergingBarChart, LinkedViews
from .layout import LayoutError, assert_no_overlap, assert_within_frame
from .scene import ResearchScene
from .templates import PROJECT_TEMPLATES, ProjectTemplate, get_template, template_names
from .theme import ECON_DARK, VideoTheme

__all__ = [
    "AgentToken",
    "ECON_DARK",
    "ChoiceMap",
    "CityLaborMarket",
    "CausalChain",
    "DivergingBarChart",
    "EquationBuild",
    "ImpulseResponsePlot",
    "LayoutError",
    "LinkedViews",
    "PROJECT_TEMPLATES",
    "ProjectTemplate",
    "ResearchScene",
    "ResultTable",
    "ShockDistribution",
    "VideoTheme",
    "WorkerToken",
    "adjustment_route",
    "assert_no_overlap",
    "assert_within_frame",
    "get_template",
    "template_names",
]

__version__ = "0.1.0"
