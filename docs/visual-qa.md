# Visual and timing QA

Rendering without an exception is necessary, not sufficient.

## The review loop

1. Render cheaply:

   ```bash
   uv run econ-manim preview <project> --overlay
   ```

2. Extract declared frames:

   ```bash
   uv run econ-manim frames <project>
   ```

3. Inspect the contact sheet and individual PNGs under `build/qa/frames/`.
4. Adjust scene code or timing.
5. Repeat before rendering 1080p.

## Inspect two kinds of frames

**Settled frames** test hierarchy, spacing, labels, and legibility.

**Transition frames** catch duplicated labels, reappearing faded objects,
crossing arrows, partially transformed equations, and brief overlaps. Add key
times just before, during, and just after major transitions.

## Layout checklist

- Title and caption remain in their fixed regions.
- No object crosses the red safe-area overlay.
- Labels sit outside nodes and do not cover paths.
- Arrowheads terminate before node boundaries.
- Symmetric objects share centers, radii, and spacing.
- Axes do not stretch merely to fill available space.
- Series are directly labeled and labels do not collide.
- Source notes remain readable but subordinate.
- No decorative object competes with the economic state.

## Equation checklist

- Show words before dense notation.
- Reveal one term at a time.
- Highlight the corresponding economic margin when the term appears.
- Keep notation stable after introduction.
- Give the viewer enough time to parse each new term.

## Timing checklist

- A short sentence remains stable for at least about two seconds.
- A chart is not removed immediately after its final series appears.
- Technical welfare tables receive longer holds than section titles.
- Transitions carry conceptual meaning rather than filling time.
- The ending remains visible long enough to read the citation.

## Final media QA

```bash
uv run econ-manim render <project>
uv run econ-manim frames <project>
uv run econ-manim qa <project>
```

Confirm 1920×1080, 30 fps, nonzero duration, successful decoding, and no
unexpected audio stream in the silent master.
