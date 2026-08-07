# Patterns from the RSUE explainer

The transport-network welfare video combined a theoretical argument, a
computational method, and link-level empirical results. Its most reusable
lesson is not a particular color or equation. It is the order in which the
viewer encounters the objects.

## Reveal a geographic result in three layers

A value-encoded network map is easier to understand when the geography, the
network's extent, and the measured values do not arrive at once. First show the
economic locations. Next connect them with a neutral network skeleton. Only
then overlay line width and color for the measured link values.

`GeographicNetworkMap` exposes both intermediate layers:

```python
locations = network.location_markers(
    location_coordinates,
    color=theme.green,
)
skeleton = network.network_skeleton(
    color=theme.muted,
    opacity=0.42,
)

scene.play(FadeIn(locations))
scene.play(
    locations.animate.set_opacity(0.42),
    LaggedStart(*[Create(line) for line in skeleton]),
)

for identifiers in ranked_value_groups(values, groups=5):
    underlays, links = network.link_layers(identifiers)
    scene.play(FadeIn(underlays), *[Create(line) for line in links])
```

The location group retains a `marker_by_id` mapping and the skeleton retains a
`skeleton_by_id` mapping. Selected places and links can therefore be revisited
later with the same identifiers used by tables, scatters, and rank panels.

## Build nested formulas in one visual space

When one method nests another, reveal the benchmark first and transform it into
the extension. Do not show two completed equations side by side. Approach
braces should label the terms to the right of the equality sign, not the welfare
object being calculated.

`EquationBuild.rhs_brace` enforces that boundary:

```python
equation = EquationBuild(
    (
        ("observed traffic", theme.blue),
        ("cost transmission", theme.orange),
        ("spatial response", theme.green),
    ),
    lhs="welfare gain",
    operators=(r"\times", r"\times"),
)

traditional = equation.rhs_brace(
    "Traditional approach",
    start=0,
    stop=1,
    color=theme.blue,
)
extended = equation.rhs_brace(
    "Extended approach",
    color=theme.green,
)
```

Reveal the traditional brace, hold it, remove it, add the remaining factors,
and then reveal the extended brace. This makes inclusion visible without
temporarily labeling the left-hand side as part of either method.

## Move from mechanism to operator to computation

For recursive models, animate a local shock and at least two propagation rounds
before writing an inverse. The sequence

```text
local shock -> first propagation -> later propagation -> inverse operator
```

provides intuition for recursive market access. State clearly when the simple
inverse is only an analogy for one block of a larger equilibrium Jacobian.

The computational comparison should begin with the work performed by the
direct method. For `K` policies, a direct calculation normally factors the
Jacobian and solves `K` high-dimensional right-hand sides. It need not form a
dense inverse, but it recovers `K` full state responses. An adjoint solves one
transposed system for the welfare weights, after which each policy requires an
inner product with its local forcing vector.

Keep this as a scene-level recipe because the appropriate symbols, dimensions,
and sparsity claims depend on the paper. The reusable visual sequence is:

```text
B -> J DeltaZ = -B -> DeltaZ -> welfare projection -> K outcomes
J' ell = q -> ell' B -> K outcomes
```

Remove the direct pipeline before completing the adjoint pipeline when both do
not fit at presentation scale.

## Link empirical views by identifier

The scatter, map, projected ranks, and mechanism card should all be driven by
the same observation identifier. Reveal ranked groups before naming selected
observations. For each selected observation, locate it in the scatter and map
before displaying its rank or decomposition. During a model transition, move
the scatter first, recolor the map second, and update ranks last.

The package supports this pattern through `EvolvingScatterPlot`,
`GeographicNetworkMap`, `SelectedRankProjections`, `SelectedRankPanel`, and
`SelectedRankHistoryPanel`.

## Let speech determine the reveal rate

A section should normally make one spoken claim at a time. Write the narration
before finalizing animation durations, reveal only the object named by the
current sentence, and keep the completed visual on screen until the cue ends.
`ResearchScene.start_voiceover` and `finish_voiceover` enforce that contract and
write matching subtitles. A section fails when its animation overruns the cue,
which exposes informational density before publication.

Split a scene into event-level narration cues when several distinct layers are
revealed. A map can use separate cues for locations, network extent, traffic
intensity, and selected examples. A factorized equation can use one cue per
factor. This produces more natural narration and makes audiovisual alignment
testable rather than dependent on hand-tuned pauses.

Short citations and data sources belong in a small, left-aligned source note.
They remain available for scrutiny without competing with the active claim.
Ordinary prose should be rendered at its final font size with `ProseText` or
`fit_prose_text`; never shrink a text object or a parent group after Pango has
laid out its glyphs. `assert_prose_is_unscaled` makes that rule testable.

## End with reproducible next steps

An explainer should not end immediately after its substantive conclusion. A
short final card can point to the paper and the code without competing with the
takeaway. `PaperCodeEndSlate` provides a two-column paper/package layout:

```python
resources = PaperCodeEndSlate(
    paper_title="Paper title",
    paper_authors="Author One · Author Two",
    paper_status="Working paper\nforthcoming",
    package_name="ResearchPackage.jl",
    package_summary="Reusable code, documentation,\nand examples",
    package_url="github.com/example/ResearchPackage.jl",
    theme=theme,
)
```

Use the scene title for the call to action and hold the completed card for at
least four seconds. Keep provisional identifiers visibly provisional.

## What remains project-specific

The transport network, policy values, corridor labels, welfare formula, and
calibration are not package defaults. They remain in the paper project. The
package supplies the identifier-preserving views, reveal order, typography,
audio mixing, and QA tools needed to present comparable research transparently.
