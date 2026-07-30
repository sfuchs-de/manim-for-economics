# Visual format gallery

This short scene isolates three patterns that proved useful across the
multimodal-transport and economic-diversity explainers:

1. **Causal chain:** build the argument as a stable sequence instead of changing
   visual grammar every few seconds.
2. **Linked views:** show one economic state in two representations and reveal
   corresponding elements at the same time.
3. **Benchmark comparison:** grow each restricted result from a fixed reference
   and label values directly.

Render and inspect it with:

```bash
uv run econ-manim preview examples/format_gallery --overlay
uv run econ-manim frames examples/format_gallery
uv run econ-manim qa examples/format_gallery
```

The numeric values in the final format are illustrative. See
`data_manifest.toml`.

Repository preview:
[silent 480p video](preview/economics_format_gallery_preview.mp4) ·
[named-frame contact sheet](preview/contact_sheet.png)
