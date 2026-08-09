import pytest

from econ_manim import format_metric, format_metric_change, spoken_decimal


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (0.04, "point zero four"),
        (0.01, "point zero one"),
        (-0.03, "minus point zero three"),
        (1.25, "one point two five"),
        (12.0, "twelve point zero zero"),
    ),
)
def test_spoken_decimal_is_deterministic_for_tts(value, expected):
    assert spoken_decimal(value) == expected


def test_metric_uses_separate_display_and_speech_forms():
    metric = format_metric(
        0.04,
        display_unit="bp",
        speech_unit="basis points",
        approximate=True,
    )
    assert metric.display == "≈0.04 bp"
    assert metric.speech == "about point zero four basis points"


@pytest.mark.parametrize(
    ("value", "display", "speech"),
    (
        (0.01, "adds ≈0.01 bp", "adds about point zero one basis points"),
        (-0.03, "subtracts ≈0.03 bp", "subtracts about point zero three basis points"),
    ),
)
def test_metric_change_uses_economic_direction_words(value, display, speech):
    phrase = format_metric_change(
        value,
        display_unit="bp",
        speech_unit="basis points",
    )
    assert phrase.display == display
    assert phrase.speech == speech


@pytest.mark.parametrize("value", (float("nan"), float("inf"), float("-inf")))
def test_metric_formatting_rejects_nonfinite_values(value):
    with pytest.raises(ValueError, match="finite"):
        format_metric(value)
