import pytest

from econ_manim import IVORY, MIDNIGHT, VideoTheme, get_theme, theme_names


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92
        if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_named_themes_resolve():
    assert theme_names() == ("midnight", "ivory")
    assert get_theme("MIDNIGHT") is MIDNIGHT
    assert get_theme(" ivory ") is IVORY


def test_custom_theme_keeps_the_original_constructor_shape():
    custom = VideoTheme(
        background="#000000",
        foreground="#FFFFFF",
        muted="#CCCCCC",
        grid="#777777",
        blue="#88AAFF",
        green="#88CC99",
        orange="#FFAA66",
        rose="#FF8899",
        card="#222222",
    )
    assert custom.name == "custom"
    assert custom.title_font == "serif"
    assert custom.text_font == "sans-serif"


def test_unknown_theme_has_a_concise_error():
    with pytest.raises(ValueError, match="choose one of: midnight, ivory"):
        get_theme("sepia")


@pytest.mark.parametrize("theme", (MIDNIGHT, IVORY))
def test_text_and_semantic_accents_have_readable_contrast(theme):
    for color in (
        theme.foreground,
        theme.muted,
        theme.blue,
        theme.green,
        theme.orange,
        theme.rose,
    ):
        assert _contrast_ratio(theme.background, color) >= 4.5
