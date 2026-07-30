# Economic Diversity and the Resilience of Cities

This is a curated reconstruction of the final explainer—not the production
history. It demonstrates:

- A recurring worker-and-city visual rather than isolated charts.
- Realized local shocks identified as released data.
- Figure 3 response paths identified as digitized point estimates.
- First- and second-order welfare intuition before the published decomposition.
- Separate evaluation of positive and negative realizations in the French shock
  series.
- An adjustment-and-welfare narrative format: one worker's routes persist from
  the choice problem through the sufficient-statistic interpretation.

Paper: <https://doi.org/10.1016/j.jinteco.2025.104184>

Replication package: <https://doi.org/10.17632/hnxp6dckyp.1>

Companion article and full production video:
<https://economic-diversity-resilience-2025.sfuchs-de.chatgpt.site/>

Repository preview:
[silent 480p video](preview/economic_diversity_preview.mp4) ·
[full contact sheet](preview/contact_sheet.png) ·
[verification record](QA.md) ·
[bundled source crosswalk](SOURCES.md)

The format is generalized in
[`docs/visual-formats.md`](../../docs/visual-formats.md) and
[`templates/storyboards/agent-choice-welfare.md`](../../templates/storyboards/agent-choice-welfare.md).

Render from the repository root:

```bash
uv run econ-manim preview examples/economic_diversity --overlay
uv run econ-manim frames examples/economic_diversity
uv run econ-manim render examples/economic_diversity
uv run econ-manim qa examples/economic_diversity
```
