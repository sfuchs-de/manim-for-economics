import pytest
from manim import VGroup

from econ_manim.typography import (
    ProseText,
    assert_prose_is_unscaled,
    fit_prose_text,
    geometrically_scaled_prose,
    normalize_prose_spacing,
)


def test_normalize_prose_spacing_preserves_ordinary_spaces_after_punctuation():
    source = "Full Jacobian: labor, routes, and congestion. Next step."

    normalized = normalize_prose_spacing(source)

    assert normalized == source


def test_normalize_prose_spacing_removes_alignment_padding_and_wide_spaces():
    source = "Traditional\u2002  0.0857 bp\u00a0  #22"

    assert normalize_prose_spacing(source) == "Traditional 0.0857 bp #22"


def test_prose_text_preserves_the_unmodified_source():
    source = "Traffic: direct savings, then equilibrium adjustment."

    rendered = ProseText(source, font_size=18)

    assert rendered.source_text == source
    assert rendered.original_text == source
    assert rendered.disable_ligatures is False


def test_fit_prose_text_uses_final_font_size_instead_of_scaling():
    rendered = fit_prose_text(
        "A deliberately long title that must fit the available frame width",
        max_width=6.0,
        font_size=42,
        min_font_size=14,
    )

    assert rendered.width <= 6.0
    assert rendered.font_size < 42


def test_fit_prose_text_rejects_unreadable_fit():
    with pytest.raises(ValueError, match="wrap or shorten"):
        fit_prose_text(
            "A deliberately long title that cannot fit the available width",
            max_width=1.0,
            font_size=42,
            min_font_size=14,
        )


def test_prose_scale_guard_detects_direct_and_parent_group_scaling():
    direct = ProseText("Do not shrink laid-out prose", font_size=18)
    grouped = ProseText("A parent group can cause the same problem", font_size=18)

    direct.scale(0.8)
    container = VGroup(grouped)
    container.scale(0.9)

    assert geometrically_scaled_prose(direct) == (direct,)
    assert geometrically_scaled_prose(container) == (grouped,)
    with pytest.raises(ValueError, match="geometrically scaled"):
        assert_prose_is_unscaled(direct, container)


def test_prose_scale_guard_allows_translation_and_rotation():
    rendered = ProseText("Native-size prose", font_size=18)

    rendered.shift([1.0, -0.5, 0.0]).rotate(0.2)

    assert_prose_is_unscaled(rendered)
