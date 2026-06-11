# Session 5 Tasks — CUDA 13.3 Tile Kernel Support

## 1. Version Bump (CUDA 13.2 → 13.3)

- [ ] 1.1 Replace "CUDA 13.2" / "cuda-13.2" with "CUDA 13.3" / "cuda-13.3" in all non-docs files
- [ ] 1.2 Run deterministic check: zero 13.2 references outside docs/

## 2. Hardware Validation — Element-wise Tile Kernel

- [ ] 2.1 Write tile vector_add kernel using `__tile_global__`, `ct::bid()`, tile loads/stores
- [ ] 2.2 Compile with `nvcc -arch=sm_120` and `cuda_tile.h` — confirm compilation succeeds
- [ ] 2.3 Run kernel — confirm numerical correctness
- [ ] 2.4 Profile with `ncu --set full` — capture report
- [ ] 2.5 Extract and record metric output: occupancy, stalls, memory bandwidth, warp activity
- [ ] 2.6 Write equivalent SIMT `__global__` vector_add for comparison
- [ ] 2.7 Profile SIMT version with same ncu flags
- [ ] 2.8 Document metric differences between tile and SIMT versions

## 3. Hardware Validation — Tile GEMM (ct::mma)

- [ ] 3.1 Write tile GEMM kernel using `ct::mma()` with BF16 or FP16 inputs
- [ ] 3.2 Compile and run — confirm numerical correctness against CPU reference
- [ ] 3.3 Profile with ncu — capture tensor core pipe metrics
- [ ] 3.4 Record which smsp pipe metrics show tensor core activity for ct::mma

## 4. Hardware Validation — Tile Reduction (Atomics)

- [ ] 4.1 Write tile reduction kernel using `ct::atomic_add` (device-scope)
- [ ] 4.2 Compile and run — confirm correct sum
- [ ] 4.3 Profile with ncu — capture atomic stall metrics
- [ ] 4.4 Record atomic-related stall reasons and throughput

## 5. Hardware Validation — TMA and Hints

- [ ] 5.1 Test `cutile::hint(1200, occupancy=N)` compilation on sm_120
- [ ] 5.2 If 1200 rejected, test alternative codes (0, 1000)
- [ ] 5.3 Test TMA path: partition_view + `ct::assume_aligned(ptr, 16_ic)` + `allow_tma=true` hint
- [ ] 5.4 Document TMA availability and hint architecture code findings

## 6. Tile Kernel Programming Guide Section

- [ ] 6.1 Write "What Are Tile Kernels" subsection with SIMT vs tile comparison table
- [ ] 6.2 Write "When to Use Tiles vs SIMT" decision framework (≥3 factors)
- [ ] 6.3 Write "RTX 5090 Constraints" subsection (sm_120, shared mem, TMA, hints)
- [ ] 6.4 Write "API Quick Reference" subsection (declarations, launch, indexing, memory, primitives, atomics, hints)
- [ ] 6.5 Write "Performance Annotations for Profiling" subsection (restrict, assume_aligned, irange, partition_view → metric connections)
- [ ] 6.6 Write "Profiling Tile Kernels" subsection (how ncu output differs — from validation data)
- [ ] 6.7 Run deterministic checks on programming guide

## 7. Tile Kernel Diagnosis Patterns

- [ ] 7.1 Write Pattern R — Tile kernel low occupancy
- [ ] 7.2 Write Pattern S — Partition_view vs gather inefficiency
- [ ] 7.3 Write Pattern T — Tile MMA underutilization
- [ ] 7.4 Write Pattern U — Tile atomic contention
- [ ] 7.5 Run deterministic checks on playbook

## 8. Analysis Dimension Annotations

- [ ] 8.1 Add tile note to Dimension 1 (Occupancy)
- [ ] 8.2 Add tile note to Dimension 2 (Tail effect)
- [ ] 8.3 Add tile note to Dimension 3 (Stalls)
- [ ] 8.4 Add tile note to Dimension 4 (Tensor core)
- [ ] 8.5 Add tile note to Dimension 5 (Timeline)
- [ ] 8.6 Add tile note to Dimension 6 (Memory)

## 9. Workflow, Common Issues, Metrics, Harness

- [ ] 9.1 Add tile kernel harness/compilation variant to Phase 2 in reference/01-workflow.md
- [ ] 9.2 Add tile collection notes to Phase 3
- [ ] 9.3 Add tile pattern references to Phase 5
- [ ] 9.4 Add tile gotchas to reference/09-common-issues.md (launch syntax, cross-calling, _ic)
- [ ] 9.5 Add tile metric notes to reference/08-rtx5090-metric-names.md
- [ ] 9.6 Add tile variant section to helpers/harness_template.cu

## 10. SKILL.md and Project Contract

- [ ] 10.1 Add tile kernel mention to SKILL.md
- [ ] 10.2 Update project contract: version 1.1, CUDA 13.3, 5 sessions
- [ ] 10.3 Run all deterministic checks from session contract
