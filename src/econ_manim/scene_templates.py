"""Catalog of small, copyable scene recipes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ConfigError


@dataclass(frozen=True, slots=True)
class SceneTemplate:
    """Metadata for one paper-independent visual recipe."""

    identifier: str
    category: str
    title: str
    use_when: str
    avoid_when: str
    source_inspiration: str
    preview_class: str
    required_inputs: tuple[str, ...]
    source: str


SCENE_TEMPLATES = (
    SceneTemplate(
        identifier="mechanism.path-flow",
        category="mechanism",
        title="Path flow",
        use_when="agents, goods, funds, or information move through named alternatives",
        avoid_when="the route itself has no economic meaning",
        source_inspiration="persistent route adjustment in the multimodal explainer",
        preview_class="PathFlowRecipe",
        required_inputs=("route points", "route label", "semantic color"),
        source="templates/scenes/mechanism/path_flow",
    ),
    SceneTemplate(
        identifier="mechanism.channel-decomposition",
        category="mechanism",
        title="Channel decomposition",
        use_when="several economic margins contribute to one outcome",
        avoid_when="the channels cannot be distinguished conceptually or empirically",
        source_inspiration="channel-to-equation synthesis in both production explainers",
        preview_class="ChannelDecompositionRecipe",
        required_inputs=("channel labels", "outcome label", "semantic colors"),
        source="templates/scenes/mechanism/channel_decomposition",
    ),
    SceneTemplate(
        identifier="empirical.coefficient-intervals",
        category="empirical",
        title="Coefficient intervals",
        use_when="a small set of estimates share one estimand and reference value",
        avoid_when="the estimates use incomparable scales or baselines",
        source_inspiration="directly labeled empirical evidence in the diversity explainer",
        preview_class="CoefficientIntervalsRecipe",
        required_inputs=("labels", "estimates", "confidence bounds", "reference value"),
        source="templates/scenes/empirical/coefficient_intervals",
    ),
    SceneTemplate(
        identifier="empirical.impulse-response",
        category="empirical",
        title="Impulse response",
        use_when="responses evolve over event time or projection horizons",
        avoid_when="the horizontal dimension is not a common horizon",
        source_inspiration="heterogeneous local-projection responses in the diversity explainer",
        preview_class="ImpulseResponseRecipe",
        required_inputs=("horizons", "estimates", "confidence bounds", "event time"),
        source="templates/scenes/empirical/impulse_response",
    ),
)


def scene_template_ids() -> tuple[str, ...]:
    """Return stable recipe identifiers accepted by the CLI."""

    return tuple(template.identifier for template in SCENE_TEMPLATES)


def scene_categories() -> tuple[str, ...]:
    """Return the available scene categories in catalog order."""

    return tuple(dict.fromkeys(template.category for template in SCENE_TEMPLATES))


def get_scene_template(identifier: str) -> SceneTemplate:
    """Resolve a scene identifier or raise a concise user-facing error."""

    for template in SCENE_TEMPLATES:
        if template.identifier == identifier:
            return template
    choices = ", ".join(scene_template_ids())
    raise ConfigError(f"unknown scene template {identifier!r}; choose one of: {choices}")


def scene_template_source(identifier: str, repo_root: Path) -> Path:
    """Return the standalone mini-project for a catalog entry."""

    source = repo_root / get_scene_template(identifier).source
    if not source.is_dir():
        raise ConfigError(f"scene template source does not exist: {source}")
    return source


def scene_template_destination(identifier: str, project_root: Path) -> Path:
    """Map ``category.recipe-name`` to an importable project recipe path."""

    template = get_scene_template(identifier)
    category, name = template.identifier.split(".", 1)
    return project_root / "recipes" / category / name.replace("-", "_")
