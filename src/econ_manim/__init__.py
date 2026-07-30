"""Reusable building blocks for economics paper explainers."""

from .charts import EquationBuild, ImpulseResponsePlot, ResultTable, ShockDistribution
from .components import AgentToken, ChoiceMap, CityLaborMarket, WorkerToken, adjustment_route
from .formats import CausalChain, DivergingBarChart, LinkedViews
from .layout import LayoutError, assert_no_overlap, assert_within_frame
from .scene import ResearchScene
from .templates import PROJECT_TEMPLATES, ProjectTemplate, get_template, template_names
from .theme import (
    ECON_DARK,
    ECON_LIGHT,
    IVORY,
    MIDNIGHT,
    THEMES,
    VideoTheme,
    get_theme,
    theme_names,
)

__all__ = [
    "AgentToken",
    "ECON_DARK",
    "ECON_LIGHT",
    "ChoiceMap",
    "CityLaborMarket",
    "CausalChain",
    "DivergingBarChart",
    "EquationBuild",
    "ImpulseResponsePlot",
    "IVORY",
    "LayoutError",
    "LinkedViews",
    "MIDNIGHT",
    "PROJECT_TEMPLATES",
    "ProjectTemplate",
    "ResearchScene",
    "ResultTable",
    "ShockDistribution",
    "THEMES",
    "VideoTheme",
    "WorkerToken",
    "adjustment_route",
    "assert_no_overlap",
    "assert_within_frame",
    "get_template",
    "get_theme",
    "template_names",
    "theme_names",
]

__version__ = "0.1.0"
