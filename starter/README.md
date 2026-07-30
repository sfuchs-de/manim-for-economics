# Start your paper video here

1. Complete `paper_brief.md`.
2. Replace the illustrative row in `data/example.csv` and update
   `data_manifest.toml`.
3. Turn the brief into a timed `storyboard.md`.
4. Edit `scenes.py`.
5. From the repository root, run:

```bash
uv run econ-manim preview starter --overlay
uv run econ-manim frames starter
uv run econ-manim qa starter
```

Generated media belongs under `build/` and is not committed.
