# General research-explainer template

This is the domain-neutral fallback. If the paper follows a system mechanism or
an agent-choice-welfare argument, first compare the complete project templates:

```bash
uv run econ-manim templates
```

1. Complete `paper_brief.md`.
2. Replace the illustrative rows in `data/example.csv` and update
   `data_manifest.toml`.
3. Turn the brief into a timed `storyboard.md`.
4. Choose a narrative and visual format from `docs/visual-formats.md`.
5. Edit `scenes.py`.
6. Name the settled and transition inspection frames in `project.toml`.
7. From the repository root, run:

```bash
uv run econ-manim preview starter --overlay
uv run econ-manim frames starter
uv run econ-manim qa starter
```

Generated media belongs under `build/` and is not committed.
