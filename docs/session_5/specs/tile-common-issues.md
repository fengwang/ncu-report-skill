# Spec: NC-7 — Tile Kernel Common Issues

## ADDED Requirements

### Requirement: Launch syntax gotcha
reference/09-common-issues.md SHALL document the tile kernel launch syntax constraint.

#### Scenario: Second chevron must be 1
WHEN the tile kernel issues section is read
THEN it SHALL state that tile kernels MUST be launched with `kernel<<<blocks, 1>>>` and explain that passing any value other than 1 for the second chevron causes a compilation or runtime error

### Requirement: Cross-calling restriction
reference/09-common-issues.md SHALL document the prohibition on cross-calling between tile and SIMT functions.

#### Scenario: No cross-calling
WHEN the tile kernel issues section is read
THEN it SHALL state that `__tile_global__` and `__tile__` functions cannot call `__device__` functions, and vice versa

### Requirement: Compile-time constant requirements
reference/09-common-issues.md SHALL document the `_ic` literal suffix requirement for tile dimensions.

#### Scenario: _ic literals
WHEN the tile kernel issues section is read
THEN it SHALL explain that tile dimensions must be compile-time constants using the `_ic` suffix (e.g., `128_ic`) or `ct::integral_constant`

#### Scenario: Deterministic check
WHEN `grep -c 'tile\|Tile\|__tile_global__' reference/09-common-issues.md` is run
THEN the count SHALL be >= 2
