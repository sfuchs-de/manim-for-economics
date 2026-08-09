# Recipe brief

## Learning goal

Explain why one adjoint solve can evaluate many policy shocks for one welfare
outcome.

## Maintained algebra

The direct method solves `J dz_e = -b_e` and projects with `q`. The adjoint
solves `J' ell = q` once and evaluates `-ell' b_e` for every shock.

## Exclude

Do not say that the adjoint avoids constructing or factorizing the Jacobian.
Its computational advantage depends on having many shocks and comparatively few
outcomes.
