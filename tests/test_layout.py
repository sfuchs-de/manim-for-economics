import pytest
from manim import RIGHT, Circle

from econ_manim import ProseText, ResearchScene
from econ_manim.layout import LayoutError, assert_no_overlap, assert_within_frame


def test_object_inside_safe_frame():
    assert_within_frame(Circle(radius=1.0))


def test_object_outside_safe_frame():
    with pytest.raises(LayoutError, match="outside the safe frame"):
        assert_within_frame(Circle(radius=1.0).shift(RIGHT * 6.5))


def test_declared_overlap_is_rejected():
    with pytest.raises(LayoutError, match="overlaps"):
        assert_no_overlap(Circle(radius=1.0), Circle(radius=1.0))


def test_separated_objects_pass():
    assert_no_overlap(Circle(radius=0.5), Circle(radius=0.5).shift(RIGHT * 2.0))


def test_long_caption_wraps_without_compressing_into_one_line():
    scene = ResearchScene()
    scene.setup()
    caption = scene.make_caption(
        "Every link starts on the 45-degree line; color identifies the same "
        "welfare-gain quintile in the scatter and map. Horizontal guides show "
        "the selected links' ranks."
    )

    assert len(caption[1]) == 2
    assert caption[1].width <= 12.1
    assert caption[1].get_bottom()[1] >= -3.61
    assert len({round(float(line.font_size), 6) for line in caption[1]}) == 1


def test_source_note_is_smaller_and_left_aligned():
    scene = ResearchScene()
    scene.setup()
    note = scene.make_source_note(
        "Sources: HPMS 2012 traffic counts; 2018 Census TIGER/Line."
    )

    assert note[1].get_left()[0] < -5.5
    assert all(line.font_size == pytest.approx(13) for line in note[1])


def test_scene_resolves_portable_font_roles():
    scene = ResearchScene()
    scene.setup()

    assert scene._title_font in {"TeX Gyre Pagella", "serif"}
    assert scene._text_font in {"TeX Gyre Heros", "sans-serif"}


def test_long_title_respects_the_safe_width():
    scene = ResearchScene()
    scene.setup()
    title = scene.make_title(
        "How should we value a transportation improvement?"
    )

    assert title.width <= 12.8


def test_stage_validation_rejects_geometrically_scaled_prose():
    scene = ResearchScene()
    scene.setup()
    label = ProseText("Render prose at its final size", font_size=18).scale(0.8)

    with pytest.raises(ValueError, match="geometrically scaled"):
        scene.validate_stage(label)


def test_scene_rejects_unfinished_narration_cue():
    scene = ResearchScene()
    scene.setup()
    scene._voiceover_end = 3.0

    with pytest.raises(RuntimeError, match="unfinished narration cue"):
        scene.tear_down()
