# Install and verify

Manim for Economics uses Manim Community 0.20.1 and Python 3.11 or newer. The
repository selects Python 3.12 for a stable common environment.

For the route that bundles Python, Manim, TeX, native libraries, and fonts in
one image, use [the Docker and Dev Container guide](self-contained.md).

## 1. Install uv

Follow the current [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
Confirm:

```bash
uv --version
```

`uv` installs the requested Python version and creates an isolated `.venv`.

## 2. Install LaTeX

Manim itself can render plain text without LaTeX, but economics videos normally
need `MathTex`. Install LaTeX before running the strict doctor.

### macOS

Install [MacTeX](https://www.tug.org/mactex/) and make sure `latex` and
`dvisvgm` are on `PATH`. Manim may also need:

```bash
brew install cairo pkg-config
```

### Windows

Install [MiKTeX](https://miktex.org/download). Allow MiKTeX to install missing
packages when prompted. In PowerShell, restart the shell after installation.

### Debian or Ubuntu

```bash
sudo apt update
sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev \
  texlive-latex-base texlive-latex-extra texlive-fonts-recommended dvisvgm
```

Other Linux distributions should follow the
[Manim local installation guide](https://docs.manim.community/en/stable/installation/linux.html).

## 3. Clone and sync

```bash
git clone https://github.com/sfuchs-de/manim-for-economics.git
cd manim-for-economics
uv sync --frozen
```

The committed `uv.lock` makes the Python environment reproducible across
supported platforms.

## 4. Diagnose the environment

```bash
uv run econ-manim doctor --strict
```

Core checks must pass for Python, Manim, LaTeX, and dvisvgm. FFmpeg is optional
and only needed for the audio-mixing command. Manim 0.20.1 uses PyAV for its
normal video output.

## 5. Render the starter

```bash
uv run econ-manim themes
uv run econ-manim demo
```

Preview the same project in the light preset:

```bash
uv run econ-manim preview starter --theme ivory
```

The output is below `starter/build/`. Source files live directly in `starter/`;
do not edit generated media.

## pip fallback

If you already manage Python environments:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# macOS or Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
econ-manim doctor --strict
```

Use `python -m manim` in place of `manim` if the console entry point is not on
your shell's `PATH`.
