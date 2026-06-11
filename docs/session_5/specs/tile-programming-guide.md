# Spec: NC-3 — Tile Kernel Programming Guide Section

## ADDED Requirements

### Requirement: Tile kernel section exists
A new top-level section `## Tile Kernel Programming Model (CUDA 13.3+)` SHALL exist in `blackwell-cuda-programming.md`.

#### Scenario: Section presence
WHEN `grep -c 'Tile Kernel' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 3

### Requirement: What-are-tile-kernels subsection
The section SHALL contain a brief explanation of what tile kernels are and how they differ from SIMT.

#### Scenario: SIMT vs tile comparison
WHEN the subsection is read
THEN it SHALL include a comparison table covering: granularity, indexing, parallelism management, memory access model, and shared memory handling

### Requirement: When-to-use decision framework
The section SHALL contain a decision framework with at least 3 concrete decision factors for choosing between tile and SIMT kernels.

#### Scenario: Decision factors present
WHEN the decision framework is read
THEN it SHALL list at least 3 factors such as: kernel complexity, need for explicit warp-level control, memory access pattern regularity, and prototype speed

#### Scenario: Framework is actionable
WHEN the decision framework is read
THEN each factor SHALL have a clear recommendation (tile or SIMT) with a brief rationale

### Requirement: RTX 5090 constraints documented
The section SHALL document RTX 5090-specific constraints for tile kernels.

#### Scenario: Hardware constraints listed
WHEN the RTX 5090 constraints subsection is read
THEN it SHALL mention: sm_120 support status, 100 KB shared memory/SM limit, TMA availability status (from validation), and any optimization hint findings

### Requirement: API quick reference
The section SHALL contain a concise API reference covering the profiling-relevant tile kernel API surface.

#### Scenario: API coverage
WHEN the API reference is read
THEN it SHALL cover: declarations (`__tile_global__`, `__tile__`), launch syntax, indexing (`ct::bid()`, `ct::num_blocks()`), tile creation, memory operations (partition_view, gather/scatter, load_masked/store_masked), primitives (`ct::mma`, reductions, scans), atomics, and optimization hints

### Requirement: Performance annotations with profiling implications
The section SHALL document performance annotations and connect each to specific ncu profiling signals.

#### Scenario: Annotation-to-metric connections
WHEN the performance annotations subsection is read
THEN it SHALL document at least: `__restrict__`, `ct::assume_aligned`, `ct::irange`, and partition_view preference
AND each annotation SHALL name the ncu metric or behavior it affects

#### Scenario: Deterministic check
WHEN `grep -c '__restrict__\|assume_aligned\|irange\|partition_view' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 4

### Requirement: Profiling tile kernels subsection
The section SHALL explain how ncu output differs for tile kernels vs SIMT, grounded in hardware validation data.

#### Scenario: Metric behavior documented
WHEN the profiling subsection is read
THEN it SHALL describe: how occupancy metrics appear, what stall reasons dominate, whether warp-level metrics are meaningful, and how tensor core utilization appears for ct::mma
