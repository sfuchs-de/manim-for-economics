# Repository guidance for Codex

## Purpose

This repository turns economics papers into short Manim explainers, with or
without narration. Correct interpretation, audiovisual alignment, and visual
verification matter more than render speed.

## Read before editing a project

For an existing paper, first locate its TeX root, compiled PDF, and replication
package. Prefer the complete TeX tree over extracting notation from the PDF
alone, and inspect the replication README and result-producing scripts before
transcribing empirical values. User-provided source material normally belongs
under the ignored `source_material/` directory.

For the selected project and template, read:

1. `paper_brief.md`
2. `storyboard.md`
3. `data_manifest.toml`
4. `project.toml`
5. Its scene and data modules

If the storyboard is not yet approved, run `econ-manim templates`, compare
`docs/visual-formats.md`, and inspect the complete projects under
`templates/projects/` before proposing a custom structure.

Treat narrative template and visual theme as independent choices. Run
`econ-manim themes`, and use `self.theme` plus component `theme=` arguments
instead of hard-coding a preset in new project scenes.

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
- In narrated work, one cue should normally carry one claim and one reveal.
- Keep the completed visual visible until its narration cue ends.
- Use direct labels instead of legends when space allows.
- Keep title, stage, and caption regions stable.
- Introduce equations term by term and connect each term to the active economic
  margin.
- Use semantic colors consistently; do not add decorative gradients, icons, or
  motion.
- Prefer symmetric layouts for agents, systems, and alternatives, with arrows
  terminating cleanly outside nodes.

## Commands

```bash
uv sync
uv run econ-manim doctor --strict
uv run econ-manim demo
uv run ruff check .
uv run pytest
uv run econ-manim preview <project> --overlay
uv run econ-manim frames <project> --transition-sweep
uv run econ-manim qa <project>
uv run econ-manim render <project>
```

## Verification

- Smoke-render after any structural scene change.
- Inspect both settled frames and transitions; a clean contact sheet of only
  settled frames is insufficient.
- Name inspection frames in `project.toml`; each major beat needs a settled
  frame and each major handoff needs a transition frame.
- Check clipping, overlaps, label placement, arrow geometry, text hold times,
  and blank or duplicated frames.
- Read narrated work at normal speed and verify that every reveal begins with
  the sentence that names it; do not rely only on silent frame inspection.
- Use `ProseText` for prose, `MathTex` for mathematics, and
  `validate_stage(...)` on representative completed states.
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
- Keep included examples runnable without network access. External paper and
  replication links are provenance references, never hidden runtime inputs.
- Keep Docker, native, and Dev Container instructions synchronized when the
  environment changes.
