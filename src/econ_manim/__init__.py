"""Reusable building blocks for economics paper explainers."""

from .charts import (
    CoefficientPlot,
    EquationBuild,
    ImpulseResponsePlot,
    ResultTable,
    ShockDistribution,
)
from .components import (
    AgentToken,
    ChoiceMap,
    CityLaborMarket,
    PaperCodeEndSlate,
    WorkerToken,
    adjustment_route,
)
from .data import read_csv_rows
from .flows import PathFlow
from .formats import CausalChain, ChannelDecomposition, DivergingBarChart, LinkedViews
from .layout import LayoutError, assert_no_overlap, assert_within_frame
from .linked_empirics import (
    EvolvingScatterPlot,
    GeographicNetworkMap,
    GeographicRegion,
    NetworkInset,
    NetworkLink,
    ScatterObservation,
    SelectedRankHistoryPanel,
    SelectedRankPanel,
    SelectedRankProjections,
    ranked_value_groups,
    read_geojson_regions,
)
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
from .typography import (
    ProseText,
    assert_prose_is_unscaled,
    fit_prose_text,
    geometrically_scaled_prose,
    normalize_prose_spacing,
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
    "EvolvingScatterPlot",
    "GeographicNetworkMap",
    "GeographicRegion",
    "ImpulseResponsePlot",
    "IVORY",
    "LayoutError",
    "LinkedViews",
    "MIDNIGHT",
    "NetworkInset",
    "NetworkLink",
    "PaperCodeEndSlate",
    "PROJECT_TEMPLATES",
    "PathFlow",
    "ProseText",
    "ProjectTemplate",
    "ResearchScene",
    "ResultTable",
    "SCENE_TEMPLATES",
    "ScatterObservation",
    "SceneTemplate",
    "ShockDistribution",
    "SelectedRankHistoryPanel",
    "SelectedRankPanel",
    "SelectedRankProjections",
    "THEMES",
    "VideoTheme",
    "WorkerToken",
    "adjustment_route",
    "assert_no_overlap",
    "assert_prose_is_unscaled",
    "assert_within_frame",
    "get_template",
    "get_scene_template",
    "get_theme",
    "fit_prose_text",
    "geometrically_scaled_prose",
    "normalize_prose_spacing",
    "ranked_value_groups",
    "read_csv_rows",
    "read_geojson_regions",
    "scene_categories",
    "scene_template_ids",
    "template_names",
    "theme_names",
]

__version__ = "0.2.0"
