# Practitioner’s guide

This is the working manual for taking one research paper from a blank project
to a verified, silent explainer. It assumes that the researcher knows the paper
but may know little Python or Manim.

The central discipline is simple: settle the economics before polishing the
animation. A clean video cannot rescue an ambiguous estimand, an unsupported
welfare claim, or a number with no source.

## Recommended input: TeX plus replication files

Give Codex direct, local access to the paper’s TeX project and replication
package whenever possible. The strongest source pack contains:

- the complete Overleaf/TeX tree, including files reached through `\input`,
  `\include`, bibliography commands, and figure paths;
- the compiled PDF, which remains useful for checking final pagination and
  visual context;
- the public replication package, including the scripts and intermediate
  outputs that produce displayed results;
- disclosure-cleared author notes explaining samples, baselines, horizons,
  units, or draft-to-publication changes.

The TeX files reveal how notation is defined and how propositions, equations,
figures, tables, and appendix results relate to one another. The replication
files reveal where a displayed number came from and what transformation lies
between the raw output and the paper. Together they sharply reduce the risk of
an animation that is visually plausible but conceptually wrong.

The package can still be used with only a PDF. In that case, treat equation
reconstruction, digitized values, and ambiguous definitions as manual review
points rather than assuming that Codex has recovered them exactly.

## 1. Verify the toolchain

Choose one setup route.

### Docker

Docker is the most contained option. It includes Python, Manim, TeX, FFmpeg,
native rendering libraries, and fonts:

```bash
docker compose build
docker compose run --rm econ-manim demo
```

### Native

If the system dependencies are installed locally:

```bash
uv sync --frozen
uv run econ-manim demo
```

The demo should produce a preview and contact sheet under `starter/build/`.
Do not begin paper-specific work until the strict doctor and demo pass.

The commands below use the native form, `uv run econ-manim`. Docker users can
replace that prefix with `docker compose run --rm econ-manim`.

## 2. Decide what the video is for

A paper video is not a compressed seminar. Choose one job:

- explain a mechanism;
- make an empirical result interpretable;
- teach a method or theoretical construction;
- connect an agent’s responses to welfare or policy value;
- establish one descriptive fact and why it matters.

Write down these seven items before creating scenes:

1. The audience.
2. The opening question.
3. The one-sentence contribution.
4. The object that should remain recognizable across the video.
5. The result that carries the argument.
6. The relevant comparison, baseline, sample, and horizon.
7. The claim the video must not make.

If two plausible interpretations would change the visual story, resolve them
with the authors before implementation.

## 3. Choose narrative structure and appearance separately

Inspect the included choices:

```bash
uv run econ-manim templates
uv run econ-manim themes
```

### Narrative templates

| Template | Use it when | Persistent object |
|---|---|---|
| `general` | No specialized sequence fits the paper | Model object, treatment comparison, theorem, measurement problem, or other research object |
| `mechanism-led` | One change propagates through a system | Network, market, equilibrium, technology, or policy channel |
| `agent-choice-welfare` | Choices and responses connect to value | Household, firm, worker, institution, or other decision maker |
| `empirical-result-led` | Identifying variation connects to one central result | Estimand, comparison, or response |
| `method-theory` | One operation turns an object into a usable result | Mathematical object, estimator, sufficient statistic, or model solution |

The shorter files in `templates/storyboards/` provide the same narrative
grammars without copying their complete scene skeletons.

### Visual themes

- `midnight` is a dark navy editorial theme.
- `ivory` is a warm paper-like light theme.

Either theme works with any narrative template. Choose based on the venue,
surrounding material, and display conditions—not the paper’s field.

## 4. Create the project

For example:

```bash
uv run econ-manim new my-paper \
  --template mechanism-led \
  --theme ivory
```

The new project contains:

```text
projects/my-paper/
├── paper_brief.md
├── storyboard.md
├── data_manifest.toml
├── project.toml
├── scenes.py
└── data/
```

Work through those files in that order. `scenes.py` comes last.

## 5. Browse and copy atomic scene recipes

Project templates determine the overall argument. Atomic recipes solve one
local communication problem without deciding the rest of the video:

```bash
uv run econ-manim scenes
uv run econ-manim scenes --category empirical
uv run econ-manim preview-scene empirical.coefficient-intervals \
  --theme ivory \
  --overlay
uv run econ-manim add-scene projects/my-paper \
  empirical.coefficient-intervals
```

`add-scene` copies the recipe below `projects/my-paper/recipes/`, including its
illustrative data and a manifest fragment. It prints the import and build
function to use. It deliberately does not rewrite `scenes.py` or silently merge
provenance entries.

Use the recipe's README as a checklist:

- confirm the visual matches the paper's economic problem;
- replace illustrative inputs with released or documented digitized values;
- merge and verify the manifest entry;
- keep the persistent object and semantic colors from the project storyboard;
- render and inspect both settled and transition frames.

The [scene catalog](scene-catalog.md) groups recipes and components by opening,
mechanism, identification, evidence, method, welfare, and conclusion.

## 6. Prepare a compact source pack

Do not ask the animation code to discover the paper’s argument. Assemble a
small set of authoritative inputs:

- the paper or manuscript source;
- the abstract, introduction, and conclusion;
- the model, design, or institutional section carrying the mechanism;
- the two or three result-bearing figures, tables, or propositions;
- public replication files for displayed empirical values;
- notes defining units, samples, baselines, and horizons;
- disclosure-cleared images or data extracts, if required.

For a long paper, this compact source pack is more useful during scene work
than repeatedly searching the entire manuscript.

### Clone an Overleaf project locally

If Git access is enabled for the Overleaf project, use the Git URL shown by
Overleaf and clone it into the repository’s ignored `source_material/`
directory. For example:

```bash
mkdir -p source_material/my-paper
git clone https://git.overleaf.com/YOUR_PROJECT_ID \
  source_material/my-paper/tex
mkdir -p source_material/my-paper/replication
unzip /path/to/replication-package.zip \
  -d source_material/my-paper/replication
cp /path/to/published-paper.pdf \
  source_material/my-paper/paper.pdf
```

This produces a useful working layout:

```text
source_material/my-paper/
├── tex/
│   ├── main.tex
│   ├── sections/
│   ├── figures/
│   └── references.bib
├── paper.pdf
└── replication/
    ├── README
    ├── code/
    ├── data/
    └── output/
```

The exact TeX and replication layouts may differ. Tell Codex which file is the
TeX root and which script or README describes the replication workflow. Do not
put an Overleaf token in a prompt or embed credentials in a committed remote
URL. `source_material/` is ignored by Git, but it remains visible to Codex when
the repository is opened as the working project.

Restricted data do not belong in the repository. Export only
disclosure-cleared moments or construct a synthetic fixture with the same
schema.

## 7. Complete the paper brief

`paper_brief.md` is the editorial contract. It should answer:

- What should a viewer understand after 60–90 seconds?
- What is the mechanism in words?
- Which evidence distinguishes this paper from a generic model?
- What is measured, proved, or approximated?
- Relative to what?
- For whom?
- Over what horizon?
- Which interpretation is tempting but unsupported?

Keep notation out of the first explanation. If the mechanism cannot be stated
in ordinary economic language, the animation is not ready.

## 8. Put displayed values in local files

Classify every visual input:

- `released`: included in a public source or replication package;
- `digitized`: recovered from a published visual;
- `illustrative`: invented solely to teach a mechanism or format.

Use `actual` for released and digitized inputs and `illustrative` for synthetic
inputs. Never let an illustrative point resemble an estimate without a visible
label.

Prefer project-local CSV files over numbers repeated inside `scenes.py`:

```python
from pathlib import Path

from econ_manim import read_csv_rows

rows = read_csv_rows(
    Path(__file__).with_name("data") / "results.csv",
    required_columns=("label", "value"),
)
```

Generate the file checksum:

```bash
uv run econ-manim checksum projects/my-paper/data/results.csv
```

Then record the file in `data_manifest.toml`:

```toml
[[dataset]]
id = "main-result"
status = "released"
classification = "actual"
source_url = "DOI or stable public URL"
license = "License or documented reuse basis"
local_path = "data/results.csv"
sha256 = "checksum printed by econ-manim"
transformation = "Selection, aggregation, rescaling, or digitization steps"
displayed_values = ["Treatment: +1.4 percentage points"]
note = "Table 3, column 2; baseline is the untreated sample."
```

Run `qa` whenever a source file changes:

```bash
uv run econ-manim qa projects/my-paper
```

A checksum mismatch is a reason to investigate the source, not merely update
the manifest.

## Worked example: a published result becomes a Manim scene

The bundled
[economic-diversity example](../examples/economic_diversity/README.md) shows
the complete chain for an existing paper. One of its empirical beats visualizes
the adjustment paths reported in Figure 3 of “Economic Diversity and the
Resilience of Cities.”

### 1. Start with the source, not a hand-drawn chart

The project records the interpretation in its
[paper brief](../examples/economic_diversity/paper_brief.md) and the location of
every beat in its
[storyboard](../examples/economic_diversity/storyboard.md). The released local
shock series comes from the public replication package. The published Figure 3
central paths are explicitly classified as `digitized`, because the exact
plotted series was not used as though it were a released data file.

That distinction is visible in
[the data manifest](../examples/economic_diversity/data_manifest.toml), which
records the source, classification, checksum, transformation, displayed
series, and omitted confidence bands.

### 2. Create the paper project

For a comparable paper, create the project before asking Codex to write scenes:

```bash
uv run econ-manim new my-paper \
  --template agent-choice-welfare \
  --theme midnight
```

Then give Codex a source-specific first task:

> Use `$create-econ-paper-video`.
>
> **Goal:** Build the brief and claim-to-source crosswalk for the adjustment
> result in the existing paper.
>
> **Context:** Read `source_material/my-paper/tex/main.tex`, all included TeX
> sections, `source_material/my-paper/paper.pdf`, and the README and scripts
> under `source_material/my-paper/replication/`. Write the animation materials
> under `projects/my-paper/`.
>
> **Constraints:** Identify the estimand, sample, comparison groups, horizon,
> units, and uncertainty before selecting a chart. Prefer a released
> replication output. If a series must be digitized, label it `digitized` and
> document the procedure. Do not write Manim code yet.
>
> **Done when:** `paper_brief.md`, `storyboard.md`, and
> `data_manifest.toml` agree about the result and every displayed value has a
> source.

### 3. Export one display-ready file

Preserve the replication package unchanged. Put only the released,
disclosure-cleared, or documented digitized series needed by the animation
under `projects/my-paper/data/`. A dynamic result might use:

```csv
horizon,lower_exposure,higher_exposure
0,0.00,0.00
1,-0.08,-0.15
2,-0.12,-0.28
```

Those numbers are only a schema illustration. They must be replaced with the
paper’s values and classified correctly before use. The bundled case study’s
actual working file is
[`figure3_point_estimates.csv`](../examples/economic_diversity/data/figure3_point_estimates.csv).

Generate its checksum:

```bash
uv run econ-manim checksum projects/my-paper/data/figure3.csv
```

Replace the starter’s illustrative manifest entry with the Figure 3 entry
using the schema in Section 7. Set `status` to `released` or `digitized` as
appropriate, use `classification = "actual"`, paste the printed checksum, and
record the exact source, transformation, and displayed series.

Then validate the completed manifest:

```bash
uv run econ-manim qa projects/my-paper
```

### 4. Connect the data to a reusable visual

Load the local file once and pass the series to the component that matches the
result’s native form. Replacing the generated `scenes.py` with the following
produces one complete empirical scene while preserving the starter’s
`PaperExplainer` class name:

Before writing the component call manually, preview the closest recipe:

```bash
uv run econ-manim preview-scene empirical.impulse-response --overlay
uv run econ-manim add-scene projects/my-paper empirical.impulse-response
```

```python
from pathlib import Path

from manim import FadeIn

from econ_manim import ImpulseResponsePlot, ResearchScene, read_csv_rows

ROWS = read_csv_rows(
    Path(__file__).with_name("data") / "figure3.csv",
    required_columns=("horizon", "lower_exposure", "higher_exposure"),
)
HORIZONS = [int(row["horizon"]) for row in ROWS]
if HORIZONS != list(range(len(HORIZONS))):
    raise ValueError("ImpulseResponsePlot expects sequential horizons starting at zero")


class PaperExplainer(ResearchScene):
    def construct(self):
        lower = [float(row["lower_exposure"]) for row in ROWS]
        higher = [float(row["higher_exposure"]) for row in ROWS]
        plot = ImpulseResponsePlot(
            {
                "lower exposure": (lower, self.theme.green),
                "higher exposure": (higher, self.theme.orange),
            },
            title="response after the shock",
            x_label="periods after shock",
            theme=self.theme,
        ).move_to([0, -0.10, 0])

        self.show_title("Adjustment differs after adverse shocks")
        self.set_caption(
            "Published point estimates · state sample and uncertainty here."
        )
        self.play(FadeIn(plot), run_time=0.8)
        self.wait(3.0)
```

Because this minimal scene is shorter than the generated starter, also replace
the starter’s `[[qa.frame]]` entries in `project.toml` with times that fall
inside the new scene:

```toml
[[qa.frame]]
time = 1.6
label = "result enters"
kind = "transition"

[[qa.frame]]
time = 3.2
label = "published response paths"
kind = "settled"
```

The complete implementation is in
[the evidence chapter](../examples/economic_diversity/chapters.py); its data
loading is separated into
[`data.py`](../examples/economic_diversity/data.py), and inspection times are
declared in
[`project.toml`](../examples/economic_diversity/project.toml).

### 5. Render, inspect, and cross-check

```bash
uv run econ-manim preview projects/my-paper --overlay
uv run econ-manim frames projects/my-paper
uv run econ-manim qa projects/my-paper
```

Ask Codex to inspect the rendered settled frame and the transitions on both
sides of the result. Then ask it to compare the final labels, paths, signs,
units, horizon, and interpretation against the TeX and replication files
again. The finished scene is not verified merely because the chart rendered.

To inspect the complete real example:

```bash
uv run econ-manim preview examples/economic_diversity --overlay
uv run econ-manim frames examples/economic_diversity
uv run econ-manim qa examples/economic_diversity
```

## 9. Write the storyboard as a sequence of handoffs

Each beat needs:

- one learning goal;
- the exact on-screen words;
- one visual action;
- a reason the next beat follows;
- an evidentiary source or an `illustrative` label.

A workable first cut usually has six or seven beats:

```text
question → object → change or comparison → response
         → evidence → interpretation → conclusion
```

The sequence should follow the paper’s logic, not its section headings.

### Timing rules

- Keep a short sentence stable for roughly two seconds.
- Hold charts after the final series appears.
- Give unfamiliar notation and multi-row tables more time.
- Use motion to represent a change in the economic state.
- Remove motion that merely decorates a pause.

Declare both settled and transition inspection frames in `project.toml`:

```toml
[[qa.frame]]
time = 12.8
label = "completed treatment comparison"
kind = "settled"

[[qa.frame]]
time = 15.1
label = "comparison to mechanism handoff"
kind = "transition"
```

Transitions deserve explicit inspection because temporary overlaps often occur
between otherwise clean settled frames.

## 10. Establish the visual system with one technical beat

Implement the opening and one representative technical beat first. This is the
cheapest point to change typography, spacing, color roles, and the recurring
visual object.

Use the smallest component that expresses the economics:

| Need | Component |
|---|---|
| Stable title, stage, caption, and cleanup | `ResearchScene` |
| Sequential economic logic | `CausalChain` |
| The same state in two representations | `LinkedViews` |
| A decision maker and alternatives | `AgentToken`, `ChoiceMap` |
| A domain-specific labor-market example | `WorkerToken`, `CityLaborMarket` |
| Dynamic estimated paths | `ImpulseResponsePlot` |
| Realized shock observations | `ShockDistribution` |
| Incremental words-first decomposition | `EquationBuild` |
| Small welfare or accounting decomposition | `ResultTable` |
| Comparison with one benchmark | `DivergingBarChart` |

Access the selected palette through `self.theme`:

```python
class MyExplainer(ResearchScene):
    def construct(self):
        theme = self.theme
        self.show_title("What changes?")
        # Pass theme=theme into reusable components.
```

Do not copy a case-study object merely because it already exists. A worker,
network, or shock distribution belongs only when it matches the paper.

## 11. Use a cheap render loop

Render the representative scene:

```bash
uv run econ-manim preview projects/my-paper --overlay
uv run econ-manim frames projects/my-paper
```

Inspect the contact sheet and individual frames under
`projects/my-paper/build/qa/`.

Check:

- clipping and safe-area violations;
- competing titles or captions;
- text covering paths or nodes;
- arrowheads entering objects;
- labels that move between settled states;
- equations appearing before their economic meaning;
- charts disappearing too soon;
- faint text in either selected theme.

Fix density by reducing simultaneous content or splitting a beat. Shrinking
every object is rarely the right correction.

## 12. Complete the scenes

Once the representative beat is approved:

1. Implement only storyboarded content.
2. Preserve the recurring object across scenes.
3. Keep semantic color roles stable.
4. Introduce formal terms only when their corresponding margin is visible.
5. Render after structural changes.
6. Add transition frames when a handoff becomes more complicated.

Do not wait for the complete video before checking timing. A two-second hold
that feels adequate in code may be unreadable in the rendered sequence.

## 13. Run conceptual QA

Review the completed preview against the paper, not against the storyboard
alone.

For every displayed number verify:

- source;
- sign;
- units;
- scaling and rounding;
- sample;
- baseline or counterfactual;
- horizon;
- whether uncertainty is shown or intentionally omitted.

For every verbal result ask:

- Does the design identify this claim?
- Is a conditional result being described as universal?
- Is a local approximation being presented as exact?
- Are positive and negative realizations separate objects or components of one
  transition?
- Does the conclusion exceed the displayed evidence?

Update the brief, storyboard, manifest, and scene together when a claim
changes.

## 14. Work effectively with Codex

Give Codex one checkpoint at a time. Use four explicit fields:

```text
Goal:
Context:
Constraints:
Done when:
```

For example:

> **Goal:** Implement the opening and the main empirical beat.
>
> **Context:** Read `paper_brief.md`, `storyboard.md`,
> `data_manifest.toml`, and `project.toml`.
>
> **Constraints:** Do not change the economic interpretation or displayed
> values. Use the existing theme and components. Keep illustrative objects
> visibly labeled.
>
> **Done when:** The preview renders, settled and transition frames have been
> inspected, and no clipping, overlap, or unreadably short hold remains.

Ask Codex to report which frames it inspected. A successful Manim command is
not evidence of visual review.

The complete staged prompts are in [Use Codex](codex-workflow.md).

## 15. Produce the master

Run:

```bash
uv run ruff check .
uv run pytest
uv run econ-manim qa projects/my-paper
uv run econ-manim render projects/my-paper
uv run econ-manim frames projects/my-paper
uv run econ-manim qa projects/my-paper
```

Confirm:

- 1920×1080 output;
- 30 fps target;
- expected duration;
- successful full decode;
- no unintended audio;
- readable final citation;
- no inspection frame beyond the video duration.

Add narration or music only after the silent master is stable and the rights
are documented.

## 16. Publish the evidence with the video

Keep the public project understandable without private context. Include:

- the paper brief;
- timed storyboard;
- data manifest;
- local released or illustrative inputs;
- source and transformation notes;
- a representative contact sheet;
- a lightweight preview;
- render and QA commands;
- links to the paper and replication package;
- license and attribution information.

Do not publish restricted data, absolute private paths, a render cache, a full
iteration history, or an undocumented soundtrack.

## Paper-type recipes

### Empirical result

Lead with the comparison or variation, reveal the estimate in its native form,
and then state the estimand, sample, and baseline. Avoid rebuilding a complete
institutional history unless it is needed to interpret the design.

### Mechanism or quantitative model

Build one system, change one object, and trace propagation without resetting
the viewer’s mental map. Compare counterfactuals against one explicit
benchmark.

### Method or theory

Begin with the problem the result solves. Keep the mathematical object and its
geometric or algorithmic representation synchronized. Introduce assumptions
when they become active, not as an opening list.

### Choice, welfare, or policy value

Show the agent’s available responses before the welfare expression. Reveal
each term with the matching behavioral margin and state the baseline, horizon,
and population directly.

## Definition of done

- [ ] One contribution, one audience, and one supported conclusion.
- [ ] Every factual beat has a source.
- [ ] Every displayed data file is local and checksummed.
- [ ] Illustrative values are visibly labeled.
- [ ] The storyboard records conceptual handoffs.
- [ ] Both settled and transition frames were inspected.
- [ ] Equations enter incrementally with their economic meaning.
- [ ] No clipping, overlap, unstable labels, or malformed arrows remain.
- [ ] All numbers match the paper or released files.
- [ ] The master decodes with the expected metadata.
- [ ] Paper, replication, license, and attribution links are present.

For deeper reference, use [data integrity](data-integrity.md),
[visual formats](visual-formats.md), [themes](themes.md),
[visual QA](visual-qa.md), and [publishing](publishing.md).
