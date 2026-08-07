"""Paper-independent color and typography presets for research explainers."""

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
    title_font: str = "serif"
    text_font: str = "sans-serif"
    title_size: int = 42
    body_size: int = 27
    small_size: int = 20
    name: str = "custom"
    description: str = "Custom research-video theme"


MIDNIGHT = VideoTheme(
    name="midnight",
    description="Dark navy field with warm text and restrained academic accents",
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


IVORY = VideoTheme(
    name="ivory",
    description="Warm paper field with dark ink and saturated analytical accents",
    background="#F7F4EC",
    foreground="#24313D",
    muted="#626B75",
    grid="#C4CFDB",
    blue="#19476F",
    green="#426E49",
    orange="#A25F28",
    rose="#90353B",
    card="#E8E1D3",
)


THEMES = {
    MIDNIGHT.name: MIDNIGHT,
    IVORY.name: IVORY,
}


def theme_names() -> tuple[str, ...]:
    """Return the stable names accepted by project files and the CLI."""

    return tuple(THEMES)


def get_theme(name: str) -> VideoTheme:
    """Resolve a named preset with a concise error for user-facing tools."""

    normalized = name.strip().lower()
    try:
        return THEMES[normalized]
    except KeyError as error:
        choices = ", ".join(theme_names())
        raise ValueError(f"unknown theme {name!r}; choose one of: {choices}") from error


# Backward-compatible aliases. New projects should prefer the neutral preset
# names above or select a theme in project.toml.
ECON_DARK = MIDNIGHT
ECON_LIGHT = IVORY
