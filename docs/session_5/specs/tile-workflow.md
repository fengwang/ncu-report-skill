# Spec: NC-6 — Tile Kernel Workflow Variant

## MODIFIED Requirements

### Requirement: Phase 2 tile kernel harness variant
Phase 2 in reference/01-workflow.md SHALL include a tile kernel variant for building the profile target.

#### Scenario: Tile compilation documented
WHEN Phase 2 is read
THEN it SHALL include a tile kernel compilation command using `#include <cuda_tile.h>` and `-arch=sm_120`

#### Scenario: Launch syntax noted
WHEN Phase 2 is read
THEN it SHALL note that tile kernels launch with `kernel<<<blocks, 1>>>` (second chevron must be 1)

### Requirement: Phase 3 tile kernel collection notes
Phase 3 SHALL note any differences in ncu collection for tile kernels.

#### Scenario: Collection flags documented
WHEN Phase 3 is read
THEN it SHALL note whether the same `--set full` flag works for tile kernels or if different sections are needed (based on validation data)

### Requirement: Phase 5 tile kernel diagnosis guidance
Phase 5 SHALL reference the tile-kernel-specific diagnosis patterns.

#### Scenario: Tile patterns referenced
WHEN Phase 5 is read
THEN it SHALL direct the reader to tile-specific patterns (R–U) when the profiled kernel uses `__tile_global__`
