# Spatial policy ladder

Use this composite recipe when the same links or locations move through an ordered sequence of model specifications. `SpatialStateDataset` validates identifiers, states, units, and selected observations before `LinkedEmpiricalViews` constructs the synchronized map, scatter, and rank history.

Replace both files in `data/`, update their hashes, and preserve the stable `id` column across all states. Do not use the recipe when states use different samples or welfare units.
