import pytest

from econ_manim import (
    GeographicRegion,
    LinkedEmpiricalViews,
    NetworkLink,
    ScatterObservation,
    SpatialStateDataset,
)


def sample_dataset() -> SpatialStateDataset:
    observations = (
        ScatterObservation("a", 1.0, {"traditional": 1.0, "extended": 1.4}, "A"),
        ScatterObservation("b", 2.0, {"traditional": 2.0, "extended": 1.7}, "B"),
        ScatterObservation("c", 3.0, {"traditional": 3.0, "extended": 3.2}, "C"),
    )
    links = (
        NetworkLink("a", (0.0, 0.0), (1.0, 0.0)),
        NetworkLink("b", (1.0, 0.0), (2.0, 0.0)),
        NetworkLink("c", (2.0, 0.0), (3.0, 0.0)),
    )
    return SpatialStateDataset(
        observations,
        links,
        ("traditional", "extended"),
        "basis points",
        state_labels={"traditional": "Traditional", "extended": "Extended"},
        selected_labels={"a": "Road A", "b": "Road B"},
    )


def test_spatial_state_dataset_keeps_values_ranks_and_links_synchronized():
    dataset = sample_dataset()
    assert dataset.identifiers == ("a", "b", "c")
    assert dataset.values("extended") == {"a": 1.4, "b": 1.7, "c": 3.2}
    assert dataset.ranks("traditional") == {"c": 1, "b": 2, "a": 3}
    assert dataset.value_groups("traditional", groups=3) == (("c",), ("b",), ("a",))


def test_spatial_state_dataset_rejects_view_identifier_drift():
    dataset = sample_dataset()
    with pytest.raises(ValueError, match="exactly the same identifiers"):
        SpatialStateDataset(
            dataset.observations,
            dataset.links[:-1],
            dataset.state_order,
            dataset.unit,
        )


def test_linked_empirical_views_use_one_state_contract():
    dataset = sample_dataset()
    region = GeographicRegion(
        "study-area",
        (((-0.5, -0.5), (3.5, -0.5), (3.5, 0.5), (-0.5, 0.5)),),
    )
    views = LinkedEmpiricalViews(
        dataset,
        (region,),
        extent=(-0.5, 3.5, -0.5, 0.5),
        selected_colors={"a": "#CA6B3C", "b": "#2A9D8F"},
        rank_headers={"traditional": "Trad.", "extended": "Extended"},
    )
    assert views.current_state == "traditional"
    assert views.scatter.current_state == "traditional"
    assert views.map.values == dataset.values("traditional")
    animation = views.animate_to("extended")
    assert animation is not None
    assert len(animation.animations) == 3
    assert views.current_state == "extended"
    assert views.map.values == dataset.values("extended")


def test_linked_empirical_views_can_omit_rank_history_from_transitions():
    dataset = sample_dataset()
    region = GeographicRegion(
        "study-area",
        (((-0.5, -0.5), (3.5, -0.5), (3.5, 0.5), (-0.5, 0.5)),),
    )
    views = LinkedEmpiricalViews(
        dataset,
        (region,),
        extent=(-0.5, 3.5, -0.5, 0.5),
        selected_colors={"a": "#CA6B3C", "b": "#2A9D8F"},
        rank_headers={"traditional": "Trad.", "extended": "Extended"},
        track_rank_history=False,
    )

    animation = views.animate_to("extended")

    assert len(animation.animations) == 2
