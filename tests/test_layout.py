import pytest
from manim import RIGHT, Circle

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
