# Examples

The examples serve different purposes. Start with the format gallery when
choosing a visual form. Use the economic-diversity case study when learning how
to trace a published result from source files through a rendered video.

| Example | Role | Evidence | First command |
|---|---|---|---|
| [`format_gallery`](format_gallery/) | Component tour | Illustrative local data | `uv run econ-manim preview examples/format_gallery --overlay` |
| [`economic_diversity`](economic_diversity/) | Published-paper case study | Released and explicitly digitized public inputs | `uv run econ-manim preview examples/economic_diversity --overlay` |
| [`network_policy_ladder`](network_policy_ladder/) | Linked spatial workflow | Illustrative local data and synthetic geography | `uv run econ-manim preview examples/network_policy_ladder --overlay` |

List the same information from the command line:

```bash
uv run econ-manim examples
```

Every example contains a paper brief, timed storyboard, project configuration,
data manifest, and scene source. Published case studies and gallery projects
also retain curated previews. Generated build directories remain untracked.
