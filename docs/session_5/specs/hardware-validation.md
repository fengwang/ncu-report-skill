# Spec: NC-2 — Hardware Validation (Tile Kernel Profiling on RTX 5090)

## ADDED Requirements

### Requirement: Element-wise tile kernel compiles and runs
A tile kernel using `__tile_global__` with `#include <cuda_tile.h>` SHALL compile with `nvcc -arch=sm_120` and produce correct output on RTX 5090.

#### Scenario: Basic tile vector_add
WHEN a tile kernel performing element-wise vector addition is compiled with `nvcc -arch=sm_120 -include cuda_tile.h`
THEN compilation SHALL succeed without errors
AND execution SHALL produce numerically correct results

#### Scenario: ncu profiles tile kernel
WHEN `ncu --set full` is run against the compiled tile kernel
THEN ncu SHALL produce a report with non-empty metric sections

### Requirement: Tile GEMM with ct::mma compiles and runs
A tile kernel using `ct::mma()` SHALL compile and produce correct matrix multiplication results on RTX 5090.

#### Scenario: Tile GEMM correctness
WHEN a tile kernel performing matrix multiplication via `ct::mma()` is compiled and run
THEN the output matrix SHALL match a CPU reference within floating-point tolerance

#### Scenario: Tensor core metrics present
WHEN the tile GEMM kernel is profiled with ncu
THEN tensor core pipe metrics SHALL have non-zero values

### Requirement: Tile reduction with atomics compiles and runs
A tile kernel using `ct::atomic_add` SHALL compile and produce correct reduction results.

#### Scenario: Tile atomic reduction
WHEN a tile kernel performing parallel reduction via `ct::atomic_add` is compiled and run
THEN the output SHALL match the expected sum within tolerance

### Requirement: TMA availability validated
The status of TMA (Tensor Memory Accelerator) on sm_120 SHALL be determined and documented.

#### Scenario: TMA validation via allow_tma hint
WHEN a tile kernel uses `cutile::hint(arch, allow_tma=true)` with partition_view and `ct::assume_aligned`
THEN the compilation result (success or failure) and any runtime behavior SHALL be documented

### Requirement: Hint architecture code validated
The `cutile::hint` architecture code for sm_120 SHALL be tested.

#### Scenario: Hint with expected code 1200
WHEN `cutile::hint(1200, occupancy=N)` is compiled targeting sm_120
THEN the compilation result SHALL be documented
AND if 1200 is rejected, alternative codes (0, 1000) SHALL be tested

### Requirement: Metric comparison documented
A comparison of ncu metrics between the SIMT and tile versions of the same kernel SHALL be documented.

#### Scenario: SIMT vs tile metric diff
WHEN the same algorithm (e.g., vector_add) is profiled as both `__global__` and `__tile_global__`
THEN the differences in occupancy, stalls, memory, and compute metrics SHALL be recorded
