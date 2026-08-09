"""Deterministic font registration for native and container renders."""

from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import manimpango
import numpy as np
from manim import Mobject, Text

_NONSTANDARD_SPACE = re.compile(r"[\u00a0\u2000-\u200a\u202f\u205f\u3000]")
_REPEATED_HORIZONTAL_SPACE = re.compile(r"[ \t]+")

_BUNDLED_FONTS = {
    "sans-serif": (
        "Inter",
        tuple(
            Path(__file__).parent / "fonts" / "inter" / filename
            for filename in (
                "Inter-Regular.otf",
                "Inter-Bold.otf",
                "Inter-Italic.otf",
                "Inter-BoldItalic.otf",
            )
        ),
    ),
}

_TEX_GYRE_FONTS = {
    "serif": (
        "TeX Gyre Pagella",
        (
            "texgyrepagella-regular.otf",
            "texgyrepagella-bold.otf",
            "texgyrepagella-italic.otf",
            "texgyrepagella-bolditalic.otf",
        ),
    ),
}


def _kpsewhich(filename: str) -> str | None:
    executable = shutil.which("kpsewhich")
    if not executable:
        return None
    result = subprocess.run(
        [executable, filename],
        check=False,
        capture_output=True,
        text=True,
    )
    path = result.stdout.strip()
    return path or None


@lru_cache(maxsize=1)
def register_project_fonts() -> dict[str, str]:
    """Register project faces and return portable font-role mappings.

    Inter is bundled for screen-readable prose. Manim already requires
    TeX for mathematical labels, so the title face comes from TeX Gyre. Generic
    role names remain as fallbacks for minimal installations.
    """

    resolved = {
        role: role
        for role in {*_BUNDLED_FONTS, *_TEX_GYRE_FONTS}
    }
    available = set(manimpango.list_fonts())
    for role, (family, paths) in _BUNDLED_FONTS.items():
        if all(path.is_file() for path in paths):
            for path in paths:
                manimpango.register_font(str(path))
            available = set(manimpango.list_fonts())
        if family in available:
            resolved[role] = family
    for role, (family, filenames) in _TEX_GYRE_FONTS.items():
        paths = [_kpsewhich(filename) for filename in filenames]
        if all(paths):
            for path in paths:
                manimpango.register_font(path)
            available = set(manimpango.list_fonts())
        if family in available:
            resolved[role] = family
    return resolved


def resolve_font(font: str) -> str:
    """Resolve a generic theme role to the registered project family."""

    return register_project_fonts().get(font, font)


def normalize_prose_spacing(text: str) -> str:
    """Use ordinary spaces while preserving explicit line breaks.

    Pango shapes the complete line using the selected font's kerning, ligatures,
    and word-space metrics. Normalize pasted Unicode spaces and alignment
    padding without replacing those native metrics.
    """

    return "\n".join(
        _REPEATED_HORIZONTAL_SPACE.sub(
            " ",
            _NONSTANDARD_SPACE.sub(" ", line),
        ).strip()
        for line in text.split("\n")
    )


class ProseText(Text):
    """Text shaped natively by Pango with deterministic project fonts.

    The complete line is passed to Pango without per-character repositioning,
    preserving kerning, ligatures, punctuation spacing, and grapheme clusters.
    Mathematical notation continues to use ``MathTex``.
    """

    def __init__(self, text: str, *args, **kwargs) -> None:
        tracking_em = float(kwargs.pop("tracking_em", 0.0))
        if tracking_em != 0:
            raise ValueError(
                "manual glyph tracking is not supported; use Pango markup "
                "letter_spacing when explicit tracking is required"
            )
        kwargs.setdefault("disable_ligatures", False)
        self.source_text = text
        normalized = normalize_prose_spacing(text)
        super().__init__(normalized, *args, **kwargs)
        self.tracking_em = 0.0
        self._native_radius = self._point_radius()

    def _point_radius(self) -> float:
        points = self.get_all_points()
        if not len(points):
            return 0.0
        center = points.mean(axis=0)
        return float(np.linalg.norm(points - center, axis=1).max())

    def has_native_scale(self, *, tolerance: float = 1.0e-6) -> bool:
        """Return whether the laid-out glyphs retain their rendered size.

        Translation and rotation preserve this radius. Geometrically scaling a
        ``ProseText`` object, including through a parent ``VGroup``, does not.
        Small Pango text should be rendered at its final font size because
        scaling vector glyphs after layout creates uneven pixel spacing.
        """

        if self._native_radius == 0:
            return True
        return abs(self._point_radius() / self._native_radius - 1.0) <= tolerance


def geometrically_scaled_prose(
    mobject: Mobject,
    *,
    tolerance: float = 1.0e-6,
) -> tuple[ProseText, ...]:
    """Return prose descendants that were scaled after text layout."""

    return tuple(
        descendant
        for descendant in mobject.get_family()
        if isinstance(descendant, ProseText)
        and not descendant.has_native_scale(tolerance=tolerance)
    )


def assert_prose_is_unscaled(
    *mobjects: Mobject,
    tolerance: float = 1.0e-6,
) -> None:
    """Fail when prose was geometrically scaled instead of rendered to fit."""

    offenders = tuple(
        prose
        for mobject in mobjects
        for prose in geometrically_scaled_prose(mobject, tolerance=tolerance)
    )
    if not offenders:
        return
    examples = ", ".join(repr(prose.source_text[:45]) for prose in offenders[:3])
    raise ValueError(
        "prose was geometrically scaled after layout; use fit_prose_text or "
        f"constructor sizing instead ({examples})"
    )


def fit_prose_text(
    text: str,
    *,
    max_width: float,
    font_size: float,
    min_font_size: float = 12,
    **kwargs,
) -> ProseText:
    """Render prose at its final font size instead of scaling laid-out glyphs."""

    candidate = ProseText(text, font_size=font_size, **kwargs)
    if candidate.width <= max_width:
        return candidate

    smallest = ProseText(text, font_size=min_font_size, **kwargs)
    if smallest.width > max_width:
        raise ValueError(
            "prose does not fit at min_font_size; wrap or shorten the text "
            f"({text!r}: width={smallest.width:.3f}, "
            f"max_width={max_width:.3f}, min_font_size={min_font_size:g})"
        )

    lower = min_font_size
    upper = font_size
    fitted = smallest
    for _ in range(12):
        midpoint = (lower + upper) / 2
        trial = ProseText(text, font_size=midpoint, **kwargs)
        if trial.width <= max_width:
            fitted = trial
            lower = midpoint
        else:
            upper = midpoint
    return fitted
