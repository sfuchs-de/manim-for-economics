"""Reusable building blocks for economics paper explainers."""

from .charts import (
    CoefficientPlot,
    EquationBuild,
    ImpulseResponsePlot,
    ResultTable,
    ShockDistribution,
)
from .components import AgentToken, ChoiceMap, CityLaborMarket, WorkerToken, adjustment_route
from .data import read_csv_rows
from .flows import PathFlow
from .formats import CausalChain, ChannelDecomposition, DivergingBarChart, LinkedViews
from .layout import LayoutError, assert_no_overlap, assert_within_frame
from .scene import ResearchScene
from .scene_templates import (
    SCENE_TEMPLATES,
    SceneTemplate,
    get_scene_template,
    scene_categories,
    scene_template_ids,
)
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
    "ChannelDecomposition",
    "CoefficientPlot",
    "DivergingBarChart",
    "EquationBuild",
    "ImpulseResponsePlot",
    "IVORY",
    "LayoutError",
    "LinkedViews",
    "MIDNIGHT",
    "PROJECT_TEMPLATES",
    "PathFlow",
    "ProjectTemplate",
    "ResearchScene",
    "ResultTable",
    "SCENE_TEMPLATES",
    "SceneTemplate",
    "ShockDistribution",
    "THEMES",
    "VideoTheme",
    "WorkerToken",
    "adjustment_route",
    "assert_no_overlap",
    "assert_within_frame",
    "get_template",
    "get_scene_template",
    "get_theme",
    "read_csv_rows",
    "scene_categories",
    "scene_template_ids",
    "template_names",
    "theme_names",
]

__version__ = "0.2.0"
