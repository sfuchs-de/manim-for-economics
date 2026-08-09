"""Consistent display and narration formatting for quantitative results."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetricPhrase:
    """A quantitative label with separate visual and spoken representations."""

    display: str
    speech: str


_SMALL_NUMBERS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def _integer_words(value: int) -> str:
    if not 0 <= value < 1_000_000_000:
        raise ValueError("spoken metric integer part must be below one billion")
    if value < 20:
        return _SMALL_NUMBERS[value]
    if value < 100:
        tens, remainder = divmod(value, 10)
        return _TENS[tens] if not remainder else f"{_TENS[tens]} {_SMALL_NUMBERS[remainder]}"
    if value < 1_000:
        hundreds, remainder = divmod(value, 100)
        prefix = f"{_SMALL_NUMBERS[hundreds]} hundred"
        return prefix if not remainder else f"{prefix} {_integer_words(remainder)}"
    for scale, label in ((1_000_000, "million"), (1_000, "thousand")):
        if value >= scale:
            quotient, remainder = divmod(value, scale)
            prefix = f"{_integer_words(quotient)} {label}"
            return prefix if not remainder else f"{prefix} {_integer_words(remainder)}"
    raise AssertionError("unreachable integer formatting branch")


def spoken_decimal(
    value: float,
    *,
    decimal_places: int = 2,
    omit_leading_zero: bool = True,
) -> str:
    """Write a finite decimal as speech without relying on a TTS number parser."""

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError("spoken metrics must be finite")
    if decimal_places < 0:
        raise ValueError("decimal_places must be nonnegative")

    rendered = f"{abs(numeric_value):.{decimal_places}f}"
    integer_text, _, decimal_text = rendered.partition(".")
    integer_value = int(integer_text)
    sign = "minus " if numeric_value < 0 else ""
    if decimal_places == 0:
        return sign + _integer_words(integer_value)

    decimal_words = " ".join(_SMALL_NUMBERS[int(digit)] for digit in decimal_text)
    if omit_leading_zero and integer_value == 0:
        number = f"point {decimal_words}"
    else:
        number = f"{_integer_words(integer_value)} point {decimal_words}"
    return sign + number


def format_metric(
    value: float,
    *,
    decimal_places: int = 2,
    display_unit: str = "",
    speech_unit: str | None = None,
    approximate: bool = False,
    signed: bool = False,
) -> MetricPhrase:
    """Return concise chart text and deterministic narration for one metric."""

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError("metrics must be finite")
    if decimal_places < 0:
        raise ValueError("decimal_places must be nonnegative")

    sign = "+" if signed and numeric_value > 0 else ""
    approximation = "≈" if approximate else ""
    unit_suffix = f" {display_unit}" if display_unit else ""
    display = (
        f"{approximation}{sign}{numeric_value:.{decimal_places}f}{unit_suffix}"
    )
    speech_prefix = "about " if approximate else ""
    speech_suffix = f" {speech_unit}" if speech_unit else ""
    speech = (
        f"{speech_prefix}{spoken_decimal(numeric_value, decimal_places=decimal_places)}"
        f"{speech_suffix}"
    )
    return MetricPhrase(display=display, speech=speech)


def format_metric_change(
    value: float,
    *,
    decimal_places: int = 2,
    display_unit: str = "",
    speech_unit: str | None = None,
    approximate: bool = True,
) -> MetricPhrase:
    """Describe a signed contribution as an amount added to or subtracted from a total."""

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError("metric changes must be finite")
    if numeric_value == 0:
        metric = format_metric(
            0.0,
            decimal_places=decimal_places,
            display_unit=display_unit,
            speech_unit=speech_unit,
            approximate=approximate,
        )
        return MetricPhrase(display=f"no change ({metric.display})", speech="no change")

    action = "adds" if numeric_value > 0 else "subtracts"
    metric = format_metric(
        abs(numeric_value),
        decimal_places=decimal_places,
        display_unit=display_unit,
        speech_unit=speech_unit,
        approximate=approximate,
    )
    return MetricPhrase(
        display=f"{action} {metric.display}",
        speech=f"{action} {metric.speech}",
    )
