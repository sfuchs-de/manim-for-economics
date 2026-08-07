# Changelog

All notable changes to this repository are recorded here.

## Unreleased

### Added

- Location-first markers and neutral network skeletons for staged
  `GeographicNetworkMap` reveals.
- Right-hand-side-only labeled braces through `EquationBuild.rhs_brace`.
- `PaperCodeEndSlate` for paper and reproducible-package resource cards.
- A case-study guide to the staged-map, nested-formula, recursive-propagation,
  adjoint, linked-view, and end-slate patterns developed for the RSUE explainer.
- `EvolvingScatterPlot`, `SelectedRankPanel`, `SelectedRankProjections`,
  `NetworkInset`, and `GeographicNetworkMap` components that retain stable
  observation identifiers across model states, rankings, and spatial views.
- Deterministic `ranked_value_groups`, scatter `dot_layers`, and network
  `link_layers` for synchronized, staged reveals.
- The `empirical.evolving-scatter` recipe, with illustrative data, provenance,
  both-theme previews, and guidance for linked empirical views.
- The `empirical.geographic-network-map` recipe, with synthetic GeoJSON and
  link data, staged value-group reveals, selected-link overlays, and both-theme
  previews.
- `frames --interval SECONDS` for regular full-video inspection plus the final
  frame.
- `--no-cache` for previews, masters, recipe previews, and the bundled demo when
  imported package code or typography changes would otherwise leave stale clips.
- Portable TeX Gyre font registration and multiline captions rendered at their
  final font size.
- `ProseText`, `fit_prose_text`, and `assert_prose_is_unscaled` to preserve
  native word and character spacing and reject geometric scaling of prose.
- Narration-led section timing, subtitle generation, compact source notes, and
  configurable mixing of embedded narration with background music.
- `SelectedRankHistoryPanel` for retaining benchmark, intermediate, and final
  ranks in one readable comparison.
- Transform-safe geographic projection helpers, preventing locations or
  network skeletons created after layout from drifting away from link geometry.
- `ResearchScene.validate_stage`, unfinished-narration checks, and repository
  guards that keep bundled prose on the deterministic typography path.
- Optional scatter coordinate labels, allowing linked-view logic to run in
  minimal environments while rendered recipes retain labeled axes by default.
- Platform-stable line endings for manifested text data so exact input hashes
  remain valid on Linux, macOS, and Windows.

## 0.2.0 — 2026-07-30

### Added

- A public scene registry and four copyable recipes:
  `mechanism.path-flow`, `mechanism.channel-decomposition`,
  `empirical.coefficient-intervals`, and `empirical.impulse-response`.
- Reusable `PathFlow`, `ChannelDecomposition`, and `CoefficientPlot`
  components.
- Explicit horizons, confidence bands, and event-time markers for
  `ImpulseResponsePlot`.
- Complete `empirical-result-led` and `method-theory` paper templates.
- `scenes`, `preview-scene`, and `add-scene` CLI commands.
- Five-point transition sweeps and separate settled, transition, and combined
  contact sheets.
- A scene catalog, expanded format gallery, both-theme previews, and a
  provenance-first practitioner workflow.

### Changed

- `qa` now checks inspection coverage, configured media profiles, inspection
  times, manifests and checksums, video decoding, and silent-master audio
  expectations.
- The format gallery now covers all reusable components.

### Compatibility

- Existing component signatures and project-template commands remain
  supported.
- Python 3.11+ remains supported. Python 3.12 and Manim Community 0.20.1
  remain the documented defaults.
- No runtime dependency was added.

### Data policy

All generic recipes and paper templates use manifest-backed illustrative data.
Paper-specific results belong only in attributed case studies or user projects.

## 0.1.0 — 2026-07-30

- Initial public starter with three paper-project formats, two themes, reusable
  economics components, provenance manifests, rendering and QA commands, and
  the economic-diversity case study.
