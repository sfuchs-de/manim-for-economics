# Geographic network map

Use this recipe when geographic context helps explain why network links have
different measured values. It builds the map inside Manim from local vector
boundaries and link endpoints; it does not paste a pre-rendered map image.

The bundled example uses the paper's contiguous-U.S. highway network. The
boundaries are derived from the public-domain 2018 Census cartographic files.
The 352 physical-link segments and their traffic shares are public-safe derived
artifacts from `TransportNetworkWelfare.jl`; restricted raw network inputs are
not redistributed. `regions.geojson` contains state Polygon and MultiPolygon
features with an `STUSPS` property. `network_links.csv` contains:

- `physical_link_id`: a stable bidirectional-link identifier shared with the
  paper's tables and scatterplots;
- `longitude_a`, `latitude_a`, `longitude_b`, `latitude_b`: endpoint
  coordinates in WGS84;
- `hulten`: the sum of the two directed traffic shares, normalized by domestic
  income;
- `primitive_F`: the paper's extended welfare elasticity, retained to preserve
  the released artifact schema but not used in this traffic-map recipe.

The example first reveals unique network endpoints as economic locations, then
draws the complete road network in neutral gray, and only then overlays five
deterministic traffic quintiles from low to high. Line width and color both
encode the same traffic measure. Three verified corridors are subsequently
highlighted as overlays; highlighting does not overwrite the traffic encoding
or change the stable link identifiers.

After `econ-manim add-scene PROJECT empirical.geographic-network-map`, import:

```python
from recipes.empirical.geographic_network_map.recipe import (
    build_geographic_network_map,
)
```

## Adapting the data

Export boundaries as GeoJSON and keep only the geographic detail needed at the
video's resolution. A shapefile can be converted before rendering, for example
with `ogr2ogr -f GeoJSON regions.geojson source.shp`; GDAL is not required at
render time. Use WGS84 longitude and latitude for ordinary maps, or provide a
common projected coordinate system for both files. Update the required column
names or adapt them to the schema above. Set `extent`, `value_range`, legend
units, and source notes explicitly.

Pin the exact input files in `data_manifest.toml`. For confidential inputs,
keep the files outside Git and resolve them through a documented environment
variable. Do not fetch live tiles or silently geocode names during rendering.

## Codex prompt

> **Goal:** Build a geographic network map from the paper's released link-level
> results.
>
> **Context:** Locate the boundary file, stable link identifiers, endpoint
> coordinates, displayed values, policy unit, and source notes.
>
> **Constraints:** Use one fixed extent and scale, preserve all link IDs, reveal
> locations and the neutral network before measured values, reveal ranked
> groups deterministically, and highlight no more than four links.
>
> **Done when:** Every plotted link matches one source row, selected links use
> the same IDs as tables and scatters, both themes render legibly, and all
> declared transition frames have been inspected.
