"""Catalog of complete examples bundled with the repository."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExampleProject:
    """One complete example and the role it serves in the learning path."""

    identifier: str
    title: str
    kind: str
    evidence: str
    use_when: str
    source: str


EXAMPLE_PROJECTS = (
    ExampleProject(
        identifier="format-gallery",
        title="Visual format gallery",
        kind="component tour",
        evidence="illustrative local data",
        use_when="choosing a visual grammar before adapting a paper",
        source="examples/format_gallery",
    ),
    ExampleProject(
        identifier="economic-diversity",
        title="Economic Diversity and the Resilience of Cities",
        kind="published-paper case study",
        evidence="released and explicitly digitized public inputs",
        use_when="learning the complete paper-to-video and provenance workflow",
        source="examples/economic_diversity",
    ),
)


def example_ids() -> tuple[str, ...]:
    """Return stable identifiers for complete examples."""

    return tuple(example.identifier for example in EXAMPLE_PROJECTS)
