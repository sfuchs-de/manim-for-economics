# Use Codex to build the video

Open this repository as the project root. Codex will discover the repository
`AGENTS.md` and the shared `create-econ-paper-video` skill.

Use Plan mode while the interpretation or storyboard is unsettled. Switch to
implementation only after the brief and claim/source crosswalk are coherent.

## Prompt 1: understand the paper

> Use `$create-econ-paper-video`.
>
> **Goal:** Turn my paper into a paper brief and claim-to-source crosswalk.
>
> **Context:** The paper and replication assets are at [paths or URLs]. Read the
> project templates and the repository guidance. Run `econ-manim templates`
> and `econ-manim themes` before recommending a structure and visual system.
>
> **Constraints:** Do not write Manim code. Do not invent numbers. Separate
> released, digitized, and illustrative inputs. Flag ambiguous welfare
> baselines or sample definitions.
>
> **Done when:** `paper_brief.md` is complete and every proposed empirical claim
> points to a table, figure, or public data file.

Review the brief as an economics argument, not as marketing copy.

## Prompt 2: design the storyboard

> **Goal:** Create a 60–90 second timed storyboard from the approved brief.
>
> **Context:** Use `paper_brief.md` and `data_manifest.toml`.
>
> **Constraints:** Compare the complete projects in `templates/projects/` and
> the formats in `docs/visual-formats.md`; select one explicitly or justify the
> general template. Choose the visual theme separately. One learning goal per
> beat; reuse one research object; explain equations term by term; connect
> transitions to the economic logic.
>
> **Done when:** `storyboard.md` specifies time, on-screen words, visual action,
> conceptual handoff, and evidence for every beat; `project.toml` contains named
> settled and transition inspection frames; no factual claim is unresolved.

## Prompt 3: establish the visual system

> **Goal:** Implement only the opening and one representative technical beat.
>
> **Context:** Use the existing `econ_manim` theme and components.
>
> **Constraints:** Keep title, stage, and caption regions stable. Use direct
> labels. Preserve symmetric geometry. If two views represent the same economic
> state, reveal matching elements together. Do not create a full-quality render.
>
> **Done when:** A low-quality preview and contact sheet have been visually
> inspected for clipping, overlaps, arrow placement, and readable holds.

This is the cheapest point to change the visual language.

## Prompt 4: complete and inspect

> **Goal:** Implement the remaining approved storyboard.
>
> **Constraints:** Smoke-render after structural changes. Inspect settled and
> transition frames. Keep all factual values tied to the manifest.
>
> **Done when:** The full preview, contact sheet, and conceptual cross-check pass,
> and no text or arrow overlaps remain.

Attach the contact sheet or individual PNGs when requesting visual feedback.
Say which frames are settled states and which are transitions.

## Prompt 5: release

> **Goal:** Produce and verify the silent 1080p master.
>
> **Constraints:** Run source, data, media, and visual QA first. Do not add music
> unless its license and attribution are present in `project.toml`.
>
> **Done when:** The master decodes, metadata match the manifest, the final
> contact sheet passes, and the README identifies all released and illustrative
> material.

## What belongs where

- One-off creative direction belongs in the prompt.
- Durable repository rules belong in `AGENTS.md`.
- The repeatable paper-to-video method belongs in the shared skill.
- Live private data should be accessed through an authorized connector or local
  file, not inferred from web search.

Official background:
[Codex best practices](https://learn.chatgpt.com/guides/best-practices) and
[repository instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
