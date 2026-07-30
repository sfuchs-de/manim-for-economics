# Self-contained use

The repository is designed to work without either production-video project,
private data, custom fonts, remote images, or an external documentation site.
After the software environment has been installed, the starter, templates,
examples, data checks, previews, and QA workflow run locally.

## Most contained route: Docker

Docker supplies Python 3.12, Manim 0.20.1, LaTeX, dvisvgm, FFmpeg, Cairo,
Pango, fontconfig, and a redistributable system font. From the repository root:

```bash
docker compose build
docker compose run --rm econ-manim demo
```

The first command downloads and builds the environment once. The second
renders the bundled starter, extracts all declared inspection frames, creates a
contact sheet, validates its data manifest, and probes the resulting video.
Outputs appear under `starter/build/` on the host.

After the image has been built, the bundled demo and examples do not require
network access:

```bash
docker compose run --rm econ-manim preview examples/format_gallery --overlay
docker compose run --rm econ-manim qa examples/economic_diversity
```

To create and render a paper project:

```bash
docker compose run --rm econ-manim new my-paper \
  --template general \
  --theme ivory
docker compose run --rm econ-manim preview projects/my-paper --overlay
```

The bind mount keeps project sources and rendered output in the checkout rather
than inside an ephemeral container. On Linux, configure Docker to run with your
user ID if you do not want container-created files owned by root.

## Dev Container

The included `.devcontainer/devcontainer.json` opens the same environment in
editors that support the Dev Container specification. Its post-create check
runs the strict environment doctor automatically.

## Local route

If Python, LaTeX, Cairo, and Pango are already available, the shorter local
path is:

```bash
uv sync --frozen
uv run econ-manim demo
```

Equivalent convenience targets are:

```bash
make setup
make demo
make test
```

## What is bundled

- Every project template, theme, reusable component, and Codex workflow file.
- Runnable generic scenes and their illustrative data manifests.
- Curated preview videos and contact sheets for visual inspection.
- The economic-diversity animation code and every numeric value it displays.
- Checksummed local CSV files for the released shocks, digitized response
  paths, and welfare table.
- Tests for configuration, provenance, components, layout, themes, media, and
  repository portability.

## Deliberate external boundaries

Some dependencies cannot responsibly be copied into this repository:

- Docker images, Python packages, and operating-system libraries are fetched
  during the first environment build.
- Papers and replication packages remain linked when their licenses or size
  make redistribution inappropriate.
- Restricted microdata, undocumented fonts, and uncleared audio are excluded.
- A user must supply the paper and any paper-specific assets for a new project.

These boundaries do not affect rendering or validating the included starter
and examples. The external links provide scholarly provenance and optional
source context, not runtime inputs.
