# Empirical-result-led template

Use this project when the paper's contribution is primarily a measured effect,
descriptive fact, event study, decomposition, or heterogeneous response.

The persistent object is the estimand. The starter carries the same words and
semantic color from identifying variation through the central estimate,
dynamics, heterogeneity, and interpretation.

All bundled values are illustrative. Replace the CSV files with released or
digitized inputs and update `data_manifest.toml` before presenting the output
as evidence.

```bash
uv run econ-manim preview templates/projects/empirical-result-led --overlay
uv run econ-manim frames templates/projects/empirical-result-led
uv run econ-manim qa templates/projects/empirical-result-led
```
