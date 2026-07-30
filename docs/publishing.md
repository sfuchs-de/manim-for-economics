# Publish responsibly

## Before release

- `uv run ruff check .`
- `uv run pytest`
- `uv run econ-manim qa <project>`
- Preview and final contact sheets pass visual review.
- Every displayed result has a source.
- Every asset has a license or written permission.
- Restricted data and absolute private paths are absent.
- The silent master has the intended dimensions, duration, and frame rate.

## Keep the repository light

Commit source, small released inputs, manifests, selected frames, and a compact
preview. Do not commit Manim caches, partial movie files, full render histories,
or a `.venv`.

Use an external article, institutional page, or release asset for a full master
when the repository would otherwise become large.

## Credit

Include:

- Paper title, authors, journal, year, and DOI.
- Replication DOI and license.
- Manim Community citation.
- Repository citation.
- Music, narration, fonts, maps, and imagery.

The repository uses MIT for software and CC BY 4.0 for original documentation
and example content. See `NOTICE.md` for paper-specific terms.

## Versioning

Tag tested public snapshots:

```bash
git tag -a v0.2.0 -m "Manim for Economics v0.2.0"
git push origin v0.2.0
```

Describe changes to the starter API and example in the GitHub release notes.
There is no PyPI publication in v0.2.0.
