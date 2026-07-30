"""Catalog of copyable, paper-independent project templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ConfigError


@dataclass(frozen=True, slots=True)
class ProjectTemplate:
    """One copyable project structure and the research story it is designed for."""

    name: str
    source: str
    title: str
    use_when: str
    sequence: str
    informed_by: str
    default_theme: str


PROJECT_TEMPLATES = (
    ProjectTemplate(
        name="general",
        source="starter",
        title="General research explainer",
        use_when="the paper does not fit a more specific narrative grammar",
        sequence="question → object → argument → result → interpretation",
        informed_by="shared lessons from both production videos",
        default_theme="midnight",
    ),
    ProjectTemplate(
        name="mechanism-led",
        source="templates/projects/mechanism-led",
        title="Mechanism-led system explainer",
        use_when="one intervention propagates through a system or equilibrium",
        sequence="question → build → perturb → trace → compare → synthesize",
        informed_by="the multimodal-transport explainer",
        default_theme="ivory",
    ),
    ProjectTemplate(
        name="agent-choice-welfare",
        source="templates/projects/agent-choice-welfare",
        title="Agent, choice, and welfare explainer",
        use_when="agent responses connect a choice menu to welfare or policy",
        sequence="agent → change → choices → evidence → decomposition → welfare",
        informed_by="the economic-diversity explainer",
        default_theme="midnight",
    ),
    ProjectTemplate(
        name="empirical-result-led",
        source="templates/projects/empirical-result-led",
        title="Empirical-result-led explainer",
        use_when="one estimand connects identifying variation to evidence and interpretation",
        sequence="question → variation → estimate → dynamics → heterogeneity → interpretation",
        informed_by="empirical continuity lessons from the economic-diversity explainer",
        default_theme="midnight",
    ),
    ProjectTemplate(
        name="method-theory",
        source="templates/projects/method-theory",
        title="Method- or theory-led explainer",
        use_when="one mathematical or economic object is transformed into a usable result",
        sequence="problem → object → operation → result → comparative static → application",
        informed_by="words-first equation and model-comparison lessons from both explainers",
        default_theme="ivory",
    ),
)


def template_names() -> tuple[str, ...]:
    """Return stable CLI names for all supported templates."""

    return tuple(template.name for template in PROJECT_TEMPLATES)


def get_template(name: str) -> ProjectTemplate:
    """Resolve a template name or raise a concise user-facing error."""

    for template in PROJECT_TEMPLATES:
        if template.name == name:
            return template
    choices = ", ".join(template_names())
    raise ConfigError(f"unknown template {name!r}; choose one of: {choices}")


def template_source(name: str, repo_root: Path) -> Path:
    """Return the on-disk source directory for a template."""

    template = get_template(name)
    source = repo_root / template.source
    if not source.is_dir():
        raise ConfigError(f"template source does not exist: {source}")
    return source
