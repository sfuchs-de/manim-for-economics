"""A sparse scene base with stable title, stage, and caption regions."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

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
    VGroup,
)

from .layout import assert_within_frame
from .media import probe_audio_duration
from .theme import ECON_DARK, VideoTheme, get_theme
from .typography import ProseText as Text
from .typography import fit_prose_text, resolve_font


class ResearchScene(Scene):
    """Base scene for non-narrated academic explainers."""

    theme: VideoTheme = ECON_DARK

    def setup(self) -> None:
        selected_theme = os.getenv("ECON_MANIM_THEME", "").strip()
        if selected_theme:
            self.theme = get_theme(selected_theme)
        self._title_font = resolve_font(self.theme.title_font)
        self._text_font = resolve_font(self.theme.text_font)
        Text.set_default(font=self._text_font)
        self.camera.background_color = self.theme.background
        self._title_group = VGroup()
        self._caption_group = VGroup()
        self._voiceover_end: float | None = None
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
        title_mobject = fit_prose_text(
            title,
            max_width=12.8,
            font=self._title_font,
            font_size=self.theme.title_size,
            color=self.theme.foreground,
            weight="BOLD",
        )
        title_mobject.move_to([0, 3.28, 0])
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
        # Render captions at their final font size. Scaling a long Pango line
        # after layout makes small-text spacing visibly uneven in video output.
        wrap_width = 88
        while True:
            lines = textwrap.wrap(
                text,
                width=wrap_width,
                break_long_words=False,
                break_on_hyphens=False,
            ) or [""]
            caption = VGroup(
                *[
                    Text(
                        line,
                        font=self._text_font,
                        font_size=self.theme.small_size,
                        color=color or self.theme.muted,
                    )
                    for line in lines
                ]
            ).arrange(DOWN, buff=0.08)
            if caption.width <= 12.1 or wrap_width <= 56:
                break
            wrap_width -= 8
        caption.move_to([0, -3.34 if len(lines) > 1 else -3.42, 0])
        rule = Line(LEFT * 6.35, RIGHT * 6.35, color=self.theme.grid, stroke_width=1.0)
        rule.next_to(caption, UP, buff=0.16 if len(lines) > 1 else 0.20)
        group = VGroup(rule, caption)
        assert_within_frame(group, y_limit=3.72, name="caption")
        return group

    def make_source_note(self, text: str, *, color: str | None = None) -> VGroup:
        """Build a small, left-aligned citation or data-source note.

        Source notes are visually subordinate to explanatory captions. Keeping
        them in a separate style prevents a citation line from competing with
        the equation or figure that carries the argument.
        """

        lines = textwrap.wrap(
            text,
            width=120,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        note = VGroup(
            *[
                Text(
                    line,
                    font=self._text_font,
                    font_size=13,
                    color=color or self.theme.muted,
                )
                for line in lines
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        rule = Line(LEFT * 6.35, RIGHT * 6.35, color=self.theme.grid, stroke_width=0.8)
        rule.move_to([0, -3.12 if len(lines) > 1 else -3.22, 0])
        note.next_to(rule, DOWN, aligned_edge=LEFT, buff=0.12)
        note.shift(RIGHT * 0.02)
        group = VGroup(rule, note)
        assert_within_frame(group, y_limit=3.72, name="source note")
        return group

    def start_voiceover(
        self,
        audio: str | Path | None = None,
        *,
        text: str | None = None,
        duration: float | None = None,
        gain: float | None = None,
    ) -> float:
        """Start one narration cue and return its duration.

        The scene continues to animate while the cue plays. Call
        :meth:`finish_voiceover` before beginning the next cue so that the
        narration, rather than arbitrary waits, determines the section length.
        """

        if self._voiceover_end is not None:
            raise RuntimeError("finish the current voiceover before starting another")
        if audio is None and duration is None:
            raise ValueError("voiceover requires an audio file or an explicit duration")
        if audio is not None:
            source = Path(audio).expanduser().resolve()
            audio_duration = probe_audio_duration(source)
            if duration is not None and abs(audio_duration - duration) > 0.10:
                raise ValueError("declared narration duration does not match its audio")
            duration = audio_duration
            self.add_sound(str(source), gain=gain)
        assert duration is not None
        if duration <= 0:
            raise ValueError("voiceover duration must be positive")
        if text:
            self.add_subcaption(text, duration=duration)
        self._voiceover_end = self.time + duration
        return duration

    def finish_voiceover(
        self,
        *,
        padding: float = 0.35,
        overrun_tolerance: float = 0.20,
    ) -> None:
        """Hold the final state until narration ends and fail on visual overrun."""

        if self._voiceover_end is None:
            return
        remaining = self._voiceover_end - self.time
        self._voiceover_end = None
        if remaining < -overrun_tolerance:
            raise ValueError(
                "visual section exceeds its narration cue by "
                f"{-remaining:.2f}s; shorten the animation or lengthen the narration"
            )
        if remaining > 0:
            self.wait(remaining)
        if padding > 0:
            self.wait(padding)

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
