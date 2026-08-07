# Linked empirical views

Many economics videos compare the same units under several assumptions. The
viewer should be able to follow an observation, not merely see one cloud fade
into another. The `EvolvingScatterPlot`, `SelectedRankPanel`,
`SelectedRankProjections`, `NetworkInset`, and `GeographicNetworkMap`
components use one stable identifier across the chart, ranking, and map.

The atomic `empirical.evolving-scatter` recipe demonstrates the pattern with
illustrative data. A paper-specific project should supply one table containing
the fixed benchmark and every vertical state. Ranks are then recomputed from
that table. This prevents drift between separately prepared figures and text.

The atomic `empirical.geographic-network-map` recipe demonstrates the map side
of the same contract. It reads local GeoJSON boundaries and a link CSV, reveals
links in deterministic value groups, and highlights selected links without
replacing the value encoding. Its bundled demonstration uses public Census
boundaries and public-safe derived traffic measures for 352 links in the U.S.
highway application. Restricted raw network inputs are not included. The
recipe can be copied independently of the evolving scatter.

For a network application, the map should show the complete distribution of
link-level results rather than only the observations discussed in the
narrative. `NetworkInset` accepts a value for every link and encodes it through
color and width. Selected observations are drawn as overlays, so their
identities remain visible as the underlying map changes across model states.

Use `GeographicNetworkMap` when geographic context is part of the argument. It
reads local Polygon or MultiPolygon boundaries through
`read_geojson_regions`, projects those boundaries and the network in the same
coordinate system, and constructs the scale and legend inside Manim. Link
width and color can encode the same supplied value. They can also be separated:
`values` then controls width, while `color_values` and `color_range` control
color. This is useful when line width should retain the welfare level but color
should identify a discrete quantile. Because the roads remain Manim objects,
the scene can draw the network progressively, transform it between model
states, and isolate a selected link without inserting a pre-rendered map.
Pin the boundary file and its hash in the project data manifest; do not depend
on a live tile service during rendering.

```python
regions = read_geojson_regions("data/states.geojson", identifier_property="STUSPS")
traffic_map = GeographicNetworkMap(
    regions,
    links,
    values=traffic_share_by_link,
    extent=(-125, -66, 24, 50),
    value_range=(0, 12),
    legend_title="Traffic share (basis points)",
    legend_ticks=(0, 5, 10),
)
self.play(FadeIn(traffic_map[:3]))
self.play(
    FadeIn(traffic_map.road_underlays),
    LaggedStart(*[Create(link) for link in traffic_map.road_lines]),
    FadeIn(traffic_map.legend),
)
```

The `extent` and `value_range` are explicit, so a sequence of maps can retain
one geographic frame and one quantitative scale. Set `show_legend=False` and
`show_graticule=False` for a compact map linked to a scatter or ranking panel.
To give the map and scatter one discrete encoding, pass the same identifier-to-
color mapping through `EvolvingScatterPlot(state_colors=...)` and the same
quantile indices through `GeographicNetworkMap(color_values=...,
color_range=(1, 5))`. Subsequent calls to `animate_values` may update raw values
and quantile indices together. Selected observations can retain a distinct
outline color without replacing their quantile fill.

When a dense network should build in ordered groups, derive those groups once
and use them in both views. `ranked_value_groups` creates nearly equal groups
with deterministic tie-breaking. `dot_layers` and `link_layers` then return the
existing Manim objects, so the reveal does not duplicate or recompute them.

```python
groups = ranked_value_groups(welfare_by_link, groups=5)
for identifiers in groups:
    underlays, links = network.link_layers(identifiers)
    self.play(
        FadeIn(scatter.dot_layers(identifiers)),
        FadeIn(underlays),
        LaggedStart(*[Create(link) for link in links]),
    )
```

Use a few groups when the viewer needs the distribution before the highlighted
cases. Introduce selected links only after the full map and scatter are visible,
then keep each identifier and semantic color fixed across every view.

For a small set of emphasized observations, `SelectedRankProjections` draws a
horizontal guide from each dot to the welfare axis and labels the intercept
with the observation's rank. Calling `animate_to(state)` moves the guide and
recomputes the rank from the same state column used by the scatter. This makes
re-ranking visible in the chart without treating rank as a second coordinate.
For long state names or changing rank labels, fade the labels out while the
points move and restore them after `animate_to`. This avoids asking Pango to
morph one line of text into another. The bundled recipe implements that
sequence.

## Current Manim choices

The package targets Manim Community 0.20.1. A moderate cross-section can use
ordinary `Dot` objects, which preserve identity and allow selected observations
to carry different colors and trails. For much larger clouds, a point-cloud
representation may render faster, but it gives up some per-observation control.

Native scene sections divide one render into named beats. `ValueTracker`,
updaters, and `always_redraw` remain useful when a model parameter changes
continuously. For discrete model closures, direct transforms are easier to
audit because each target comes from a named column in the data.

Two maintained extensions are useful but remain optional. Manim Voiceover can
time animations to narration bookmarks and reuse narration as subtitles.
Manim Slides can turn sectioned scenes into live presentations or exported web
and PowerPoint formats. Neither belongs in the core dependency set because the
silent deterministic render should continue to work without audio services or
presentation software.

Official references:

- [Manim Community 0.20.1 documentation](https://docs.manim.community/en/stable/)
- [Value trackers and updaters](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.html)
- [Scene sections](https://docs.manim.community/en/stable/reference/manim.scene.section.html)
- [Manim Voiceover](https://voiceover.manim.community/en/stable/)
- [Manim Slides](https://manim-slides.eertmans.be/latest/)

## Next reusable recipes

One useful next addition would combine the evolving scatter and network inset into a
single spatial-biography recipe. One selected observation would remain linked
to its map segment, trajectory, mechanism values, and rank. A parameter-sweep
recipe could then move all observations continuously as an elasticity changes,
with the mean effect and rank correlation updating from the same parameter
tracker.

A rank-flow recipe would be useful when the main result is a policy-ordering
change rather than a level change. A network-impulse recipe could start from one
improved edge and reveal how market-access effects spread across neighboring
nodes. An adjoint-sweep recipe should compare an \(n\)-by-\(E\) matrix of direct
state responses with the single \(n\)-vector welfare adjoint. It should state
the computational contract precisely: construct and factor the equilibrium
Jacobian once, solve the transposed system for the welfare adjoint, and then
evaluate all policy derivatives as inner products with the forcing matrix.
Finally, a section-to-slides export command and an optional
voiceover-bookmark adapter would make the same scene usable in a narrated video
and a seminar without maintaining separate animation code.
