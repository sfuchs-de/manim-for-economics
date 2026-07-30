---
name: create-econ-paper-video
description: Turn an economics paper, draft, replication package, or research result into a concise Manim explainer with a paper brief, timed storyboard, verified empirical claims, reusable economics visuals, low-cost render iteration, conceptual review, and final media QA. Use when Codex is asked to plan, create, revise, render, or audit an economics paper video or a Manim research explainer.
---

# Create an Economics Paper Video

Build the economic argument before building the animation. Treat source
integrity, visual inspection, and timing as required deliverables.

Use [the practitioner’s guide](../../../docs/practitioners-guide.md) as the
end-to-end operating sequence. The checkpoints below define the required
Codex review gates.

## Workflow

### 1. Inspect the paper and assets

- Locate the paper source or PDF, replication files, existing figures, fonts,
  and media.
- Compare the project templates with `uv run econ-manim templates` and choose a
  narrative grammar because it matches the paper's contribution.
- Compare the visual presets with `uv run econ-manim themes`. Choose appearance
  separately from narrative structure and viewing context.
- Read the selected project's `project.toml`, `paper_brief.md`,
  `storyboard.md`, and `data_manifest.toml`.
- Identify the persistent research object, central change or comparison,
  mechanism or design, result-bearing tables or figures, and—only when
  relevant—the agent, choice set, shock, or welfare baseline.
- Classify every proposed input as `released`, `digitized`, or `illustrative`.
- Do not expose restricted data or infer missing values.

Read [conceptual-integrity.md](references/conceptual-integrity.md) when the
video contains empirical estimates, welfare results, or a sufficient statistic.

### 2. Complete the paper brief

- State the contribution in one sentence.
- Explain the mechanism without notation.
- Record the audience and what it can be assumed to know.
- Define the relevant estimand, theorem, welfare object, or policy
  interpretation, including its baseline, horizon, and sample where applicable.
- List claims the design does not support.

Do not write scene code while material interpretations remain unresolved.

### 3. Build the timed storyboard

- Compare the narrative formats in `docs/visual-formats.md` and select one
  because it fits the contribution.
- Start from a complete project in `templates/projects/` or a copyable
  storyboard in `templates/storyboards/`.
- Use six or seven beats with one learning goal each.
- Reuse one economic object across beats.
- Record time, on-screen words, visual action, transition logic, and source.
- Introduce equations term by term and activate the matching economic margin.
- Budget longer holds for unfamiliar notation and multi-row results.
- Declare named `settled` and `transition` inspection frames in `project.toml`.

Read [checkpoint-criteria.md](references/checkpoint-criteria.md) before treating
the storyboard as approved.

### 4. Establish one representative scene

- Reuse `ResearchScene`, `VideoTheme`, and the smallest relevant components.
- Use `self.theme` and pass it into components; do not bind paper content to a
  preset palette.
- Keep title, stage, and caption regions stable.
- Prefer direct labels, symmetric geometry, restrained arrows, and semantic
  color.
- When two views show the same economic state, reveal corresponding elements at
  the same time.
- Implement the opening and one technical beat before expanding the full video.
- Run:

```bash
uv run econ-manim preview <project> --overlay
uv run econ-manim frames <project>
```

Inspect the images. Successful compilation is not visual QA.

### 5. Complete and iterate

- Implement only storyboarded content.
- Smoke-render after structural changes.
- Sample settled frames and frames inside each major transition.
- Review clipping, overlaps, duplicated objects, arrows, axes, label stability,
  equation density, and text hold time.
- Compare all on-screen claims with the paper and manifest again.

Read [visual-review.md](references/visual-review.md) for the inspection pass.

### 6. Produce the delivery master

Run:

```bash
uv run ruff check .
uv run pytest
uv run econ-manim qa <project>
uv run econ-manim render <project>
uv run econ-manim frames <project>
uv run econ-manim qa <project>
```

Verify dimensions, frame rate, duration, decoding, final frames, and absence of
unexpected audio. Add music or narration only when the project's audio fields
contain a track, license, and attribution.

## Defaults

- Prefer a silent, text-led 16:9 explainer.
- Prefer a 60–90 second first cut.
- Prefer a words-first equation build over displaying the full derivation.
- Prefer released data; use clearly labeled illustrative values only for
  mechanisms.
- Keep generated media below `build/`.
- Never publish a full render history, private paths, restricted data, or
  undocumented audio.
