"""A sparse scene base with stable title, stage, and caption regions."""

from __future__ import annotations

import os

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
)

from .layout import assert_within_frame
from .theme import ECON_DARK, VideoTheme


class ResearchScene(Scene):
    """Base scene for non-narrated academic explainers."""

    theme: VideoTheme = ECON_DARK

    def setup(self) -> None:
        self.camera.background_color = self.theme.background
        self._title_group = VGroup()
        self._caption_group = VGroup()
        if os.getenv("ECON_MANIM_QA", "0") == "1":
            self.add(self.safe_area_overlay())

    def safe_area_overlay(self) -> VGroup:
        """Return a non-filled title-safe rectangle and region guides."""

        frame = Rectangle(
            width=13.40,
            height=7.30,
            color=self.theme.rose,
            stroke_width=1.0,
            fill_opacity=0,
        )
        top = Line(LEFT * 6.70, RIGHT * 6.70, color=self.theme.grid, stroke_width=0.8)
        top.move_to([0, 2.72, 0])
        bottom = top.copy().move_to([0, -2.82, 0])
        frame.set_stroke(opacity=0.55)
        top.set_stroke(opacity=0.45)
        bottom.set_stroke(opacity=0.45)
        return VGroup(frame, top, bottom)

    def remove_group(self, group: VGroup) -> None:
        """Remove a group whether Manim registered it or its children on scene."""

        self.remove(group, *group.submobjects)

    def make_title(self, title: str, kicker: str | None = None) -> VGroup:
        title_mobject = Text(
            title,
            font_size=self.theme.title_size,
            color=self.theme.foreground,
            weight="BOLD",
        ).move_to([0, 3.28, 0])
        parts = [title_mobject]
        if kicker:
            kicker_mobject = Text(kicker.upper(), font_size=16, color=self.theme.muted)
            kicker_mobject.next_to(title_mobject, UP, buff=0.10)
            parts.insert(0, kicker_mobject)
        group = VGroup(*parts)
        assert_within_frame(group, y_limit=3.72, name="title")
        return group

    def show_title(self, title: str, kicker: str | None = None, *, run_time: float = 0.7):
        new_title = self.make_title(title, kicker)
        if len(self._title_group):
            self.remove_group(self._title_group)
            if len(self._caption_group):
                self.remove_group(self._caption_group)
            self.play(FadeIn(new_title, shift=DOWN * 0.04), run_time=run_time)
            self._caption_group = VGroup()
        else:
            self.play(FadeIn(new_title, shift=DOWN * 0.08), run_time=run_time)
        self._title_group = new_title
        return new_title

    def make_caption(self, text: str, *, color: str | None = None) -> VGroup:
        caption = Text(
            text,
            font_size=self.theme.small_size,
            color=color or self.theme.muted,
        )
        if caption.width > 12.1:
            caption.scale_to_fit_width(12.1)
        caption.move_to([0, -3.42, 0])
        rule = Line(LEFT * 6.35, RIGHT * 6.35, color=self.theme.grid, stroke_width=1.0)
        rule.next_to(caption, UP, buff=0.20)
        group = VGroup(rule, caption)
        assert_within_frame(group, y_limit=3.72, name="caption")
        return group

    def set_caption(self, text: str, *, color: str | None = None, run_time: float = 0.45):
        new_caption = self.make_caption(text, color=color)
        if len(self._caption_group):
            self.remove_group(self._caption_group)
            self.play(FadeIn(new_caption), run_time=run_time)
        else:
            self.play(Create(new_caption[0]), FadeIn(new_caption[1]), run_time=run_time)
        self._caption_group = new_caption
        return new_caption

    def clear_stage(self, *mobjects, run_time: float = 0.45) -> None:
        """Fade only the supplied stage objects, preserving title and caption."""

        visible = [mobject for mobject in mobjects if mobject is not None]
        if visible:
            self.play(*[FadeOut(mobject) for mobject in visible], run_time=run_time)
