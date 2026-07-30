# Bundled source crosswalk

The paper and full replication package remain external for licensing and size
reasons. Everything required to reproduce the values shown in the animation is
included locally:

| Animation beat | Local source | Classification | Original source |
|---|---|---|---|
| Released city-year shocks | `data/bartik_selected.csv` | Released, actual | Public replication package |
| Negative-shock response paths | `data/figure3_point_estimates.csv` | Digitized, actual | Published Figure 3 |
| Positive and negative welfare rows | `data/table2_welfare.csv` | Released, actual | Published Table 2 |

`data_manifest.toml` records the source URLs, transformations, displayed
values, licenses, and SHA-256 checksums. `econ-manim qa
examples/economic_diversity` verifies every local file without downloading
anything.

## Claims represented in the video

- Workers can adjust within a city, across cities, or through employment.
- Economic diversity expands the set of nearby sector–occupation alternatives.
- The empirical design combines predetermined local exposure with common
  national growth and estimates dynamic responses with local-projection IV.
- Published negative-shock paths are more adverse at higher HHI.
- The welfare calculation combines a first-order response with a second-order
  term capturing curvature and co-movement across adjustment margins.
- The displayed welfare rows are separate averages for positive and negative
  realized French shocks, evaluated relative to baseline. They are not two
  pieces of one national transition.

See `paper_brief.md` for the interpretation, `storyboard.md` for the narrative
crosswalk, and `QA.md` for the verification record.
