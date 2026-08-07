# Atomic scene recipes

Atomic recipes solve one recurring communication problem without prescribing a
paper's full narrative. List them with:

```bash
uv run econ-manim scenes
```

Preview a recipe independently of your project:

```bash
uv run econ-manim preview-scene mechanism.path-flow --theme ivory
```

Copy one into an existing project:

```bash
uv run econ-manim add-scene projects/my-paper empirical.coefficient-intervals
```

The command copies code, local illustrative data, and a manifest fragment. It
does not rewrite the project's scene or silently merge provenance records.

## Mechanism

- [`mechanism.path-flow`](mechanism/path_flow/): trace economically meaningful
  movement while one system remains fixed.
- [`mechanism.channel-decomposition`](mechanism/channel_decomposition/):
  connect distinct margins to one outcome.

## Empirical evidence

- [`empirical.coefficient-intervals`](empirical/coefficient_intervals/): compare
  a small set of estimates on one honest scale.
- [`empirical.impulse-response`](empirical/impulse_response/): show a dynamic
  response with uncertainty and an event marker.
- [`empirical.evolving-scatter`](empirical/evolving_scatter/): follow a fixed
  sample through ordered model states while recomputing selected ranks.
- [`empirical.geographic-network-map`](empirical/geographic_network_map/):
  construct a vector basemap and reveal value-encoded links in ranked groups.

Bundled numerical examples are illustrative unless a recipe says otherwise.
The geographic-network-map recipe is the exception: it ships with public-safe
derived U.S. highway artifacts and a source manifest. Any replacement data must
likewise record released or digitized provenance before the recipe is factual.
