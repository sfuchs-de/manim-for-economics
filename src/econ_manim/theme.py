"""Color and typography tokens shared by the starter and examples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VideoTheme:
    """A restrained semantic palette for a research explainer."""

    background: str
    foreground: str
    muted: str
    grid: str
    blue: str
    green: str
    orange: str
    rose: str
    card: str
    title_size: int = 42
    body_size: int = 27
    small_size: int = 20


ECON_DARK = VideoTheme(
    background="#101922",
    foreground="#F1E9DA",
    muted="#9DAAB7",
    grid="#405163",
    blue="#79AFDE",
    green="#7EB28A",
    orange="#D8904B",
    rose="#D87878",
    card="#172430",
)
