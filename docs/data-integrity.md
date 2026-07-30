# Protect data and conceptual integrity

An attractive chart can still be wrong. Treat the data manifest as part of the
animation.

## Status vocabulary

- `released`: directly available in a public source or replication package.
- `digitized`: recovered from a published visual; record the figure and omit
  false precision.
- `illustrative`: invented solely to explain a mechanism.

Do not use `released` for confidential data, an author's private extract, or a
number remembered from a draft.

## Manifest requirements

Each non-illustrative entry needs:

- `classification = "actual"`; synthetic mechanism data use `illustrative`.
- Stable source URL or DOI.
- License or reuse basis.
- Local path when a file is included.
- SHA-256 checksum for included files.
- A `transformation` describing selection, aggregation, rescaling, or
  digitization.
- A `displayed_values` list naming the exact values or series that reach the
  screen.

Illustrative entries use both `status = "illustrative"` and
`classification = "illustrative"`. Released and digitized entries must be
classified as actual. This apparent redundancy makes accidental relabeling
harder.

Run:

```bash
uv run econ-manim qa <project>
```

The command fails when a declared file is missing or its checksum changes.

## Keep restricted data out

Commit only released inputs or small derived moments whose public redistribution
is documented. For restricted data:

- Include a schema or synthetic fixture.
- Record the secure pipeline separately.
- Export only disclosure-cleared values.
- Never place credentials, raw extracts, or secure paths in the repository.

## Cross-check the finished video

Create a table with one row per displayed number. Verify signs, units, samples,
baselines, horizons, rounding, and whether positive and negative realizations
are combined or separated.

The economic-diversity example states explicitly that its welfare rows are
average effects for workers in France from the realized shock series, split by
sign and measured relative to baseline. That qualifier is part of the result.
