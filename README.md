# Manim for Economics

Turn an economics paper into a short, rigorous Manim explainer—without starting
from an empty scene or asking an AI agent to guess what the paper means.

This repository combines:

- A sparse visual system for agents, choices, systems, shocks, impulse
  responses, causal chains, linked analytical views, benchmark comparisons,
  decompositions, and optional domain-specific labor-market objects.
- A paper brief and timed storyboard that separate economic reasoning from
  animation code.
- Provenance manifests that distinguish released, digitized, and illustrative
  inputs.
- A render/inspection CLI built around cheap previews and contact sheets.
- Independent narrative templates and light/dark visual themes.
- Durable `AGENTS.md` instructions and a shared Codex skill.
- A readable case study based on “Economic Diversity and the Resilience of
  Cities.”

The intended audience is an economist who has a paper and a visual idea, but
little or no Manim experience.

## Start from the paper, not the PDF alone

The workflow works best when Codex can inspect the paper’s source and the
files that produced its results:

- the Overleaf/TeX project, including included sections, bibliography, and
  figure sources;
- the compiled paper PDF;
- the public replication package, including scripts, output tables, and
  display-ready data;
- any author notes needed to distinguish published results from illustrative
  animation values.

Direct TeX access makes definitions, equations, labels, and cross-references
much easier to trace than a PDF alone. Replication files let Codex recover the
actual plotted series, units, samples, and transformations instead of
transcribing or guessing them.

If the paper is on Overleaf and Git access is enabled, clone it into the
ignored `source_material/` directory using the project’s Git URL:

```bash
mkdir -p source_material/my-paper
git clone https://git.overleaf.com/YOUR_PROJECT_ID \
  source_material/my-paper/tex
mkdir -p source_material/my-paper/replication
unzip /path/to/replication-package.zip \
  -d source_material/my-paper/replication
```

Use the Git URL and authentication method supplied by Overleaf. Do not put
tokens in a prompt or commit `source_material/`; the directory is ignored by
default. A PDF-only workflow is possible, but empirical and mathematical
cross-checks will require more manual review.

## See the method in one picture

![Contact sheet from the economic-diversity example](examples/economic_diversity/preview/contact_sheet.png)

The contact sheet is generated from settled and transition frames. It is a QA
artifact, not a collage designed after the fact. Named frame labels make the
intended check explicit.

## Quick start

Clone the repository. If Docker is available, the most self-contained first run
is:

```bash
docker compose build
docker compose run --rm econ-manim demo
```

This includes Python, Manim, LaTeX, dvisvgm, FFmpeg, Cairo, Pango, and a known
font inside the image. It renders the starter, extracts its QA frames, builds a
contact sheet, validates the local data, and probes the video.

For a smaller native installation, install [uv](https://docs.astral.sh/uv/) and
run:

```bash
uv sync --frozen
uv run econ-manim demo
```

Create your own project:

```bash
uv run econ-manim templates
uv run econ-manim themes
uv run econ-manim new my-paper --template general
uv run econ-manim new network-paper --template mechanism-led
uv run econ-manim new choice-paper --template agent-choice-welfare
uv run econ-manim new empirical-paper --template empirical-result-led
uv run econ-manim new method-paper --template method-theory
uv run econ-manim scenes
```

For an existing paper, a practical first pass is:

```bash
uv run econ-manim new my-paper \
  --template general \
  --theme ivory
```

Then open this repository in Codex and ask:

> Use `$create-econ-paper-video`.
>
> **Goal:** Turn the existing paper into a paper brief, claim-to-source
> crosswalk, and timed storyboard.
>
> **Context:** The TeX root is
> `source_material/my-paper/tex/main.tex`; the compiled paper and replication
> package are under `source_material/my-paper/`. The animation project is
> `projects/my-paper/`.
>
> **Constraints:** Read the TeX and replication scripts before proposing
> scenes. Do not invent or silently transcribe empirical values. Record the
> source and transformation for every displayed result. Do not write scene
> code until the brief and storyboard are coherent.
>
> **Done when:** The brief and storyboard identify one persistent visual
> object, every factual beat points to the paper or replication files, and one
> representative scene is specified for implementation.

Template and appearance can be mixed:

```bash
uv run econ-manim new network-paper \
  --template mechanism-led \
  --theme midnight
```

Then edit, in this order:

1. `projects/my-paper/paper_brief.md`
2. `projects/my-paper/data_manifest.toml`
3. `projects/my-paper/storyboard.md`
4. `projects/my-paper/scenes.py`

See [setup](docs/setup.md) for macOS, Windows, Linux, and `pip` instructions.
The [practitioner’s guide](docs/practitioners-guide.md) walks through the full
paper-to-video process, including a worked example built from an existing
paper and its replication files.

## Commands

| Command | Purpose |
|---|---|
| `econ-manim doctor` | Diagnose Python, Manim, LaTeX, fonts, and optional FFmpeg |
| `econ-manim templates` | Explain the available paper-story templates |
| `econ-manim themes` | List paper-independent visual presets |
| `econ-manim scenes` | Browse atomic visual recipes by communication problem |
| `econ-manim preview-scene ID` | Render one recipe independently in either theme |
| `econ-manim add-scene PROJECT ID` | Copy a recipe, local data, and manifest fragment into a project |
| `econ-manim checksum FILE` | Generate the SHA-256 value for a manifest input |
| `econ-manim demo` | Render and inspect the bundled starter end to end |
| `econ-manim new NAME --template TYPE --theme PRESET` | Select narrative structure and appearance independently |
| `econ-manim preview PROJECT` | Render an 854×480, 15 fps draft |
| `econ-manim preview PROJECT --overlay` | Add title-safe and content-region guides |
| `econ-manim preview PROJECT --no-cache` | Rebuild every animation fragment after shared code, font, or helper changes |
| `econ-manim frames PROJECT` | Extract declared inspection frames and a contact sheet |
| `econ-manim frames PROJECT --transition-sweep` | Build separate settled, five-point transition, and combined contact sheets |
| `econ-manim frames PROJECT --interval 5` | Sample the complete video every five seconds and include the final frame |
| `econ-manim qa PROJECT` | Check source, provenance, checksums, inspection coverage, media profile, decoding, and audio expectations |
| `econ-manim render PROJECT` | Render the silent 1920×1080, 30 fps master |
| `econ-manim audio PROJECT` | Mix documented music or narration into the master |

All generated output goes below the selected project's `build/` directory and
is ignored by Git.

## The workflow

```text
paper → brief → claim/source crosswalk → storyboard
      → one representative scene → low-quality render
      → settled + transition + interval frames → conceptual check
      → full scene → silent master → optional licensed audio
```

The expensive render is deliberately last. A full video should not be the first
time anyone sees the typography, timing, or transitions.

Use `ProseText` for prose and `MathTex` for mathematics. `ProseText` is the
package-wide Pango wrapper used by the bundled scenes; it uses the registered
project font, preserves native kerning and ligatures, and normalizes pasted or
padded spaces. When text must fit a fixed width, use `fit_prose_text` rather
than `scale_to_fit_width` on an already rendered line.

Manim's animation cache speeds up repeated scene edits, but it may retain stale
fragments after imported package code, fonts, or external helpers change. Use
`--no-cache` for the final preview and master after those changes.

## Economic-diversity example

The example is a clean reconstruction of the production narrative. It does not
include the 26 historical subclasses, approximately 1 GB of intermediate
renders, restricted worker microdata, or the uncleared soundtrack.

```bash
uv run econ-manim preview examples/economic_diversity --overlay
uv run econ-manim frames examples/economic_diversity --transition-sweep
uv run econ-manim render examples/economic_diversity
uv run econ-manim qa examples/economic_diversity
```

Read the [case-study guide](examples/economic_diversity/README.md), the
[published paper](https://doi.org/10.1016/j.jinteco.2025.104184), and the
[CC BY 4.0 replication package](https://doi.org/10.17632/hnxp6dckyp.1).

## Choose a format

Read [visual and narrative formats](docs/visual-formats.md) before writing scene
code. The [template catalog](templates/README.md) turns patterns from the
multimodal-transport and economic-diversity production videos into complete,
paper-independent project starters:

- `mechanism-led`, which keeps one system alive as a change propagates;
- `agent-choice-welfare`, which connects one decision menu to evidence and
  value;
- `empirical-result-led`, which preserves one estimand from identifying
  variation through estimates and interpretation;
- `method-theory`, which transforms one mathematical or economic object into a
  usable result;
- `general`, which makes no assumption about the paper's subject or method.

The corresponding storyboard-only files remain available for researchers who
want the narrative grammar without a complete scene skeleton. The general
starter does not require a decision maker, shock, identification strategy, or
welfare result.

Visual appearance is a separate choice. The included `midnight` and `ivory`
themes distill the diversity and multimodal production palettes without tying
either palette to a paper type. See [themes](docs/themes.md).

The [format gallery](examples/format_gallery/) is a short, paper-independent
example covering the reusable component library with explicitly illustrative
values. The [scene catalog](docs/scene-catalog.md) organizes those components by
the job they perform in a paper:

```bash
uv run econ-manim preview examples/format_gallery --overlay
uv run econ-manim frames examples/format_gallery
```

## Use Codex

Open the repository as a Codex project. The root `AGENTS.md` supplies durable
standards, while `.agents/skills/create-econ-paper-video/` supplies the staged
paper-to-video method.

A useful first request is:

> Use `$create-econ-paper-video`. Read my paper, run `econ-manim templates`, and
> recommend the closest narrative grammar. Interview me where interpretation is
> genuinely ambiguous, then produce the paper brief and a claim-to-source
> crosswalk. Do not write animation code yet.

Continue with the checkpoint prompts in
[Using Codex](docs/codex-workflow.md).

## Documentation

- [Install and verify](docs/setup.md)
- [Use the self-contained environment](docs/self-contained.md)
- [Follow the practitioner’s guide](docs/practitioners-guide.md)
- [From paper to storyboard](docs/storyboarding.md)
- [Choose visual and narrative formats](docs/visual-formats.md)
- [Browse the scene catalog](docs/scene-catalog.md)
- [Choose a visual theme](docs/themes.md)
- [Use Codex](docs/codex-workflow.md)
- [Protect data integrity](docs/data-integrity.md)
- [Run visual and timing QA](docs/visual-qa.md)
- [Link observations across model states, ranks, and maps](docs/linked-empirical-views.md)
- [Reuse the patterns developed for the RSUE explainer](docs/rsue-explainer-patterns.md)
- [Add narration or music](docs/audio.md)
- [Publish responsibly](docs/publishing.md)
- [Troubleshoot](docs/troubleshooting.md)
- [Read the changelog](CHANGELOG.md)

## License and citation

Code is MIT licensed. Original documentation and example content are CC BY 4.0.
Third-party and paper-specific provenance is recorded in [NOTICE.md](NOTICE.md).
Use `CITATION.cff` to cite the repository.

Manim Community is a separate MIT-licensed project and should also be cited
when appropriate.
