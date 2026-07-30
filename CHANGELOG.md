# Changelog

All notable changes to this repository are recorded here.

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
