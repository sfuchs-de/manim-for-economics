# Verification record

This record documents the checks behind the curated example. It is not a
substitute for the paper or replication documentation.

## Claim and data checks

- The title, mechanism, three grouped welfare margins, identification
  description, and welfare interpretation were checked against the
  [September 2025 paper](https://sfuchs-de.github.io/research/economic_resilience_v2.pdf).
- All 18 city-year rows in `data/bartik_selected.csv` match the selected rows
  in the released 2005, 2009, and 2019 Bartik-shock extracts, field for field.
- The response paths are the central estimates digitized from published Figure
  3 for horizons 0–20. The signs, HHI ordering, horizons, and verbal claim were
  checked against the figure. Confidence bands are intentionally omitted and
  the animation says so.
- The four displayed welfare rows reproduce Table 2 exactly:

| Realization | HHI decile | First order | Second order | Total |
|---|---:|---:|---:|---:|
| Negative | 1 | -1.00 | -0.06 | -1.06 |
| Negative | 10 | -2.38 | -2.55 | -4.93 |
| Positive | 1 | 7.10 | -3.25 | 3.85 |
| Positive | 10 | 12.75 | -6.94 | 5.81 |

The video identifies these as percentage changes relative to baseline for
realized French shocks averaged by HHI bin, accumulated over 2006Q1–2019Q4
through horizon 20 with a discount factor of 0.99.

## Visual and timing checks

The final 1080p master was sampled at 19 declared times spanning settled states
and chapter transitions. Native-resolution checks covered the worker routes,
released-shock distribution, sufficient-statistic build, both welfare tables,
and conclusion. The final pass found no clipping, undeclared overlap, garbled
title transitions, or objects outside the title-safe frame.

## Media checks

The delivery master has:

- 1920×1080 dimensions.
- 30 fps target frame rate.
- 64.06-second duration.
- No audio stream.
- Successful full-stream decode.

The committed preview is a silent 854×480, 15 fps transcode of that master.

## Deliberate exclusions

No restricted worker microdata, private replication paths, historical render
chain, paper PDF, or soundtrack is included.
