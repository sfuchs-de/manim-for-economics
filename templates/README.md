# Template catalog

Templates encode a narrative grammar, not a discipline or dataset. Pick the one
whose sequence matches the paper's contribution.

Themes are independent. Use `--theme midnight` or `--theme ivory` with any
template; the defaults below merely reproduce the contrast between the two
reference videos.

## Complete project templates

| CLI name | Best fit | Narrative sequence | Production lesson |
|---|---|---|---|
| `general` | Papers without one dominant grammar | question → object → argument → result → interpretation | Shared continuity and QA conventions |
| `mechanism-led` | Networks, equilibrium propagation, policy transmission, model channels | question → build → perturb → trace → compare → synthesize | The multimodal explainer keeps one system alive across the video |
| `agent-choice-welfare` | Choice, adjustment, treatment responses, insurance, welfare, policy value | agent → change → choices → evidence → decomposition → welfare | The diversity explainer connects one menu to evidence and welfare |

```bash
uv run econ-manim templates
uv run econ-manim themes
uv run econ-manim new my-paper --template mechanism-led
uv run econ-manim new my-other-paper --template agent-choice-welfare
uv run econ-manim new light-choice-paper \
  --template agent-choice-welfare \
  --theme ivory
```

Each command creates a complete project with its own brief, storyboard,
manifest, scene skeleton, and named QA frames.

### General preview

![General template contact sheet](../starter/preview/contact_sheet.png)

[Watch the silent preview](../starter/preview/general_preview.mp4).

### Mechanism-led preview

![Mechanism-led template contact sheet](projects/mechanism-led/preview/contact_sheet.png)

[Watch the silent preview](projects/mechanism-led/preview/mechanism_led_preview.mp4).

### Agent-choice-welfare preview

![Agent-choice-welfare template contact sheet](projects/agent-choice-welfare/preview/contact_sheet.png)

[Watch the silent preview](projects/agent-choice-welfare/preview/agent_choice_welfare_preview.mp4).

## Storyboard-only templates

The `storyboards/` folder also includes:

- `empirical-result-led.md` for estimates, event studies, descriptive facts,
  and decompositions;
- `method-theory.md` for theorems, estimators, algorithms, sufficient
  statistics, and identification results.

Start those projects with `--template general`, then replace its storyboard with
the relevant file. They remain storyboard-only because empirical and
methodological papers vary too much for one honest visual skeleton.

## What to preserve

From the multimodal format, preserve the system's spatial identity while its
state changes. From the diversity format, preserve the alternatives and their
semantic colors as the story moves from decisions to estimates and value.

Do not copy the subject matter. A node need not be a transport mode, and an
agent need not be a worker.
