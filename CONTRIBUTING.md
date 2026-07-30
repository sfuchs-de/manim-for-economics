# Contributing

Contributions should make the paper-to-video workflow clearer, more reliable,
or more economically useful.

## Development

```bash
uv sync
uv run ruff check .
uv run pytest
uv run econ-manim preview starter --overlay
```

Keep reusable components small and composable. Add a component only when it
solves a repeated economics-communication problem; avoid turning the starter
into a general charting framework.

New visual formats should include a minimal gallery scene, named settled and
transition inspection frames, and an explicit statement about whether any
displayed values are released, digitized, or illustrative.

## Pull requests

Explain:

- The user problem.
- The behavior or documentation changed.
- The commands and renders used for verification.
- Any new data or asset provenance.

Do not include generated media except for a deliberately curated preview.
