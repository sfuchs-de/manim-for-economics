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
        identifier="mechanism.additive-waterfall",
        category="mechanism",
        title="Additive waterfall",
        use_when="mechanisms add to or subtract from one benchmark in common units",
        avoid_when="the terms are multiplicative factors or use incomparable units",
        source_inspiration="signed welfare decomposition in the network-welfare explainer",
        preview_class="AdditiveWaterfallRecipe",
        required_inputs=(
            "exact benchmark value",
            "signed mechanism changes",
            "common unit",
            "final result label",
        ),
        source="templates/scenes/mechanism/additive_waterfall",
    ),
    SceneTemplate(
        identifier="mechanism.network-impulse",
        category="mechanism",
        title="Recursive network impulse",
        use_when="one local shock propagates through repeated network responses",
        avoid_when="the displayed rounds do not correspond to a defined linearized operator",
        source_inspiration="market-access propagation in the network-welfare explainer",
        preview_class="NetworkImpulseRecipe",
        required_inputs=(
            "network geometry",
            "initial shock",
            "round-specific responses",
            "recursion interpretation",
        ),
        source="templates/scenes/mechanism/network_impulse",
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
    SceneTemplate(
        identifier="empirical.evolving-scatter",
        category="empirical",
        title="Evolving scatter",
        use_when="the same observations move through ordered model specifications",
        avoid_when="states use different samples, units, or horizontal benchmarks",
        source_inspiration="model-ladder and link-ranking comparisons in network welfare",
        preview_class="EvolvingScatterRecipe",
        required_inputs=(
            "stable identifiers",
            "fixed benchmark",
            "state values",
            "selected labels",
        ),
        source="templates/scenes/empirical/evolving_scatter",
    ),
    SceneTemplate(
        identifier="empirical.geographic-network-map",
        category="empirical",
        title="Geographic network map",
        use_when="link-level values need geographic context and selected corridors",
        avoid_when="coordinates, boundaries, or link identifiers are unverified",
        source_inspiration="ranked traffic and welfare maps in network appraisal",
        preview_class="GeographicNetworkMapRecipe",
        required_inputs=(
            "GeoJSON boundaries",
            "stable link identifiers",
            "endpoint coordinates",
            "link values and units",
        ),
        source="templates/scenes/empirical/geographic_network_map",
    ),
    SceneTemplate(
        identifier="empirical.spatial-policy-ladder",
        category="empirical",
        title="Spatial policy ladder",
        use_when="the same links move through ordered model specifications",
        avoid_when="states use different samples, identifiers, or welfare units",
        source_inspiration="synchronized map, scatter, and rank changes in network welfare",
        preview_class="SpatialPolicyLadderRecipe",
        required_inputs=(
            "stable link identifiers",
            "link geometry",
            "common benchmark and state values",
            "selected observations",
        ),
        source="templates/scenes/empirical/spatial_policy_ladder",
    ),
    SceneTemplate(
        identifier="empirical.selected-observation-biography",
        category="empirical",
        title="Selected observation biography",
        use_when="one link or location explains a consequential ranking change",
        avoid_when="the selected object changes definition across model states",
        source_inspiration="corridor biographies in linked network-welfare views",
        preview_class="SelectedObservationBiographyRecipe",
        required_inputs=(
            "stable observation identifier",
            "link geometry",
            "state values and ranks",
            "verified observation label",
        ),
        source="templates/scenes/empirical/selected_observation_biography",
    ),
    SceneTemplate(
        identifier="method.adjoint-sweep",
        category="method",
        title="Adjoint policy sweep",
        use_when="many policy shocks are evaluated for one or a few scalar outcomes",
        avoid_when="the number of outcomes is comparable to or larger than the number of shocks",
        source_inspiration="one-adjoint welfare evaluation in the network-welfare explainer",
        preview_class="AdjointSweepRecipe",
        required_inputs=(
            "equilibrium Jacobian",
            "policy forcing vectors",
            "outcome gradient",
            "dimension comparison",
        ),
        source="templates/scenes/method/adjoint_sweep",
    ),
    SceneTemplate(
        identifier="method.linearization-to-adjoint",
        category="method",
        title="Linearization to adjoint",
        use_when="the audience needs the derivation connecting equilibrium to an adjoint sweep",
        avoid_when="the Jacobian, forcing vector, or welfare projection is not defined",
        source_inspiration="the staged IFT and adjoint argument in network welfare",
        preview_class="LinearizationToAdjointRecipe",
        required_inputs=(
            "equilibrium residual",
            "Jacobian and policy forcing",
            "welfare gradient",
            "paper-specific sign convention",
        ),
        source="templates/scenes/method/linearization_to_adjoint",
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
