# Session 5 Brainstorming — CUDA 13.3 Tile Kernel Support

## Decisions

| ID | Question | Choice | Rationale |
|---|---|---|---|
| D1 | ENVIRONMENT.md has stale CUDA 13.2 ref but is outside blast radius | Add ENVIRONMENT.md to allowed_files | Simple fix, satisfies deterministic check |
| D2 | Validation strategy for tile kernel ncu metrics | Progressive 3-kernel: element-wise → GEMM/mma → reduction/atomics | Addresses adversarial concern about trivial-only validation |
| D3 | Harness template tile kernel integration | Add tile variant section to existing harness_template.cu | One file, both SIMT and tile side-by-side, no new top-level files |
| D4 | Task ordering given unknown tile kernel ncu behavior | Validate first, then write content | Content must be grounded in real hardware data, not hypothetical |

## Key Clarifications

- **Tile kernels ≠ thread block clusters.** Tile kernels (`__tile_global__`, `cuda_tile.h`) are a higher-level programming model where code operates on tile blocks and the compiler manages thread-level parallelism. Clusters are a separate (orthogonal) hardware feature already documented in Session 4.
- **Additive content.** Existing SIMT content is unchanged. Tile kernel content is added alongside, not replacing.
- **Validation-first ordering.** Because ncu behavior for tile kernels is completely unknown, we run hardware validation before writing content to avoid hypothetical patterns that may be contradicted by real data.
