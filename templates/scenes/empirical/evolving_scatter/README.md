# Evolving scatter

Use this recipe when the same observations can be evaluated under an ordered
set of model specifications. The horizontal benchmark remains fixed while the
vertical values and selected ranks update from the same source table.

Inputs:

- one stable observation identifier;
- a common horizontal benchmark;
- one vertical value for every named state;
- short labels and semantic colors for a small set of observations to follow.

The bundled values are illustrative.

The recipe first reveals observations in three benchmark-rank groups. This
lets the viewer read the distribution before the selected cases and their
ranks appear. Change the number of groups, not the stable identifiers, when
adapting the cadence to a larger sample.

After `econ-manim add-scene PROJECT empirical.evolving-scatter`, import:

```python
from recipes.empirical.evolving_scatter.recipe import build_evolving_scatter
```

For spatial applications, pair the scatter with `NetworkInset` using the same
identifiers. This keeps map highlights, dot trajectories, and ranks tied to one
observation rather than to manually copied labels.

## Codex prompt

> **Goal:** Show how the paper's benchmark observations change under successive
> model mechanisms.
>
> **Context:** Locate the machine-readable result table that contains all
> states, identifiers, labels, and units.
>
> **Constraints:** Keep the sample and horizontal benchmark fixed. Recompute
> ranks from each state rather than transcribing them. Highlight no more than
> four observations at once.
>
> **Done when:** Every dot retains its identity through each transition, the
> rank panel agrees with the plotted values, and transition frames have been
> inspected.
