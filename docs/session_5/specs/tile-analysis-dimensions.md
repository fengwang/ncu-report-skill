# Spec: NC-5 — Tile Kernel Analysis Dimension Annotations

## MODIFIED Requirements

### Requirement: Dimension 1 (Occupancy) tile annotation
Dimension 1 SHALL include a tile kernel note explaining how occupancy behaves when the compiler manages warps.

#### Scenario: Tile occupancy note exists
WHEN Dimension 1 in reference/05-analysis-dimensions.md is read
THEN it SHALL contain a subsection or note addressing tile kernel occupancy
AND it SHALL explain that the programmer does not control warp count directly — the compiler determines thread/warp allocation based on tile shape

### Requirement: Dimension 2 (Tail effect) tile annotation
Dimension 2 SHALL note whether tail effect analysis applies to tile kernels.

#### Scenario: Tile tail effect note exists
WHEN Dimension 2 is read
THEN it SHALL address whether grid-level tail effects apply to tile kernels (they do — tile kernels still launch with a grid of blocks)

### Requirement: Dimension 3 (Stalls) tile annotation
Dimension 3 SHALL note how stall signatures differ for tile kernels.

#### Scenario: Tile stall note exists
WHEN Dimension 3 is read
THEN it SHALL note that warp divergence stalls are eliminated (compiler manages control flow) and describe what stall reasons are expected to dominate (from validation data)

### Requirement: Dimension 4 (Tensor core) tile annotation
Dimension 4 SHALL note how ct::mma maps to tensor core metrics.

#### Scenario: Tile tensor core note exists
WHEN Dimension 4 is read
THEN it SHALL explain that ct::mma() is the tile API for tensor core operations and note which smsp pipe metrics indicate tensor core activity (from validation data)

### Requirement: Dimension 5 (Timeline) tile annotation
Dimension 5 SHALL note any differences in SM utilization timeline for tile kernels.

#### Scenario: Tile timeline note exists
WHEN Dimension 5 is read
THEN it SHALL address whether the timeline dimension applies unchanged or has tile-specific considerations

### Requirement: Dimension 6 (Memory) tile annotation
Dimension 6 SHALL note how tile-level memory operations affect cache efficiency metrics.

#### Scenario: Tile memory note exists
WHEN Dimension 6 is read
THEN it SHALL explain that partition_view enables structured/TMA-eligible access while gather/scatter produces irregular patterns, and note implications for coalescing and L2 hit rate metrics
