# Visual and timing QA

Rendering without an exception is necessary, not sufficient.

## The review loop

1. Render cheaply:

   ```bash
   uv run econ-manim preview <project> --overlay
   ```

2. Extract declared frames and sweep each transition:

   ```bash
   uv run econ-manim frames <project> --transition-sweep
   ```

3. Inspect:
   - `build/qa/settled_states.png`;
   - `build/qa/transition_sweep.png`;
   - `build/qa/contact_sheet.png`;
   - the full-resolution PNGs under `build/qa/frames/`.
4. Adjust scene code or timing.
5. Repeat before rendering 1080p.

## Inspect two kinds of frames

**Settled frames** test hierarchy, spacing, labels, and legibility.

**Transition frames** catch duplicated labels, reappearing faded objects,
crossing arrows, partially transformed equations, and brief overlaps. The
transition sweep samples every declared transition at `t−0.50`, `t−0.25`, `t`,
`t+0.25`, and `t+0.50` seconds, clamped to the video duration.

Name both types in `project.toml` so the contact sheet states what each frame is
meant to verify:

```toml
[[qa.frame]]
time = 8.2
label = "completed choice menu"
kind = "settled"

[[qa.frame]]
time = 10.4
label = "choice menu to response chart"
kind = "transition"
```

The older `render.key_times` list remains supported by the basic `frames`
command. Named frames are required for transition sweeps and complete QA.
`econ-manim qa` requires at least one settled and one transition frame and
rejects named frames that lie beyond the rendered duration.

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
uv run econ-manim frames <project> --transition-sweep
uv run econ-manim qa <project>
```

The QA command confirms that the video matches either the configured preview or
master dimensions and frame rate, that opening and midpoint frames decode, and
that the silent preview or master has no unexpected audio stream.
