# Repository guidance for Codex

## Purpose

This repository turns economics papers into short, non-narrated Manim
explainers. Correct interpretation and visual verification matter more than
render speed.

## Read before editing a project

For the selected project, read:

1. `paper_brief.md`
2. `storyboard.md`
3. `data_manifest.toml`
4. `project.toml`
5. Its scene and data modules

Do not implement unresolved economic interpretations. Ask for a decision when
two readings would materially change the story.

## Data and claims

- Never invent coefficients, data points, sample definitions, baselines, or
  welfare interpretations.
- Label each input `released`, `digitized`, or `illustrative` in the manifest.
- Classify each input separately as `actual` or `illustrative`.
- Preserve raw inputs. Record transformations and checksums.
- If a visual is schematic, say so in the scene or its nearby documentation.
- Cross-check every displayed empirical value against its cited table, figure,
  or public file.

## Visual conventions

- One learning goal per beat.
- Use direct labels instead of legends when space allows.
- Keep title, stage, and caption regions stable.
- Introduce equations term by term and connect each term to the active economic
  margin.
- Use semantic colors consistently; do not add decorative gradients, icons, or
  motion.
- Prefer symmetric city and worker layouts with arrows terminating cleanly
  outside nodes.

## Commands

```bash
uv sync
uv run econ-manim doctor --strict
uv run ruff check .
uv run pytest
uv run econ-manim preview <project> --overlay
uv run econ-manim frames <project>
uv run econ-manim qa <project>
uv run econ-manim render <project>
```

## Verification

- Smoke-render after any structural scene change.
- Inspect both settled frames and transitions; a clean contact sheet of only
  settled frames is insufficient.
- Check clipping, overlaps, label placement, arrow geometry, text hold times,
  and blank or duplicated frames.
- Do not claim completion from successful Python compilation alone.
- Render 1080p only after the preview and contact sheet pass.
- Exclude generated `build/` and `media/` directories unless a curated preview
  is explicitly intended for publication.

## Repository boundaries

- The reusable public API lives under `src/econ_manim/`.
- User-facing guidance lives under `docs/`, not inside the skill.
- The shared staged method lives in
  `.agents/skills/create-econ-paper-video/`.
- Do not add the original case-study version history, confidential data, or
  unlicensed audio.
