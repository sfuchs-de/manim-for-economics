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

Some recipes coordinate several views because their evidence is meaningful
only when stable observation identifiers, model states, and selected ranks
move together. These composite recipes remain copyable units: they validate one
shared dataset and expose the coordinated transition through package components
rather than duplicating synchronization logic in a paper project.

## Mechanism

- [`mechanism.path-flow`](mechanism/path_flow/): trace economically meaningful
  movement while one system remains fixed.
- [`mechanism.channel-decomposition`](mechanism/channel_decomposition/):
  connect distinct margins to one outcome.
- [`mechanism.additive-waterfall`](mechanism/additive_waterfall/): move from a
  benchmark to a final result through signed changes in common units.
- [`mechanism.network-impulse`](mechanism/network_impulse/): trace a local
  shock through successive rounds of a recursive network response.

## Method

- [`method.adjoint-sweep`](method/adjoint_sweep/): replace one state solve per
  policy shock with one transposed solve and sparse policy inner products.
- [`method.linearization-to-adjoint`](method/linearization_to_adjoint/): derive
  the adjoint progressively from an equilibrium residual, its linearization,
  and the welfare projection.

## Empirical evidence

- [`empirical.coefficient-intervals`](empirical/coefficient_intervals/): compare
  a small set of estimates on one honest scale.
- [`empirical.impulse-response`](empirical/impulse_response/): show a dynamic
  response with uncertainty and an event marker.
- [`empirical.evolving-scatter`](empirical/evolving_scatter/): follow a fixed
  sample through ordered model states while recomputing selected ranks.
- [`empirical.geographic-network-map`](empirical/geographic_network_map/):
  construct a vector basemap and reveal value-encoded links in ranked groups.
- [`empirical.spatial-policy-ladder`](empirical/spatial_policy_ladder/): update
  a map, scatter, and selected-rank history from one validated spatial-state
  dataset.
- [`empirical.selected-observation-biography`](empirical/selected_observation_biography/):
  trace one selected link across model states without losing its spatial or
  empirical identity.

Bundled numerical examples are illustrative unless a recipe says otherwise.
Any replacement data must record released or digitized provenance before the
recipe is presented as factual.
