# Session 5: CUDA 13.3 Upgrade — Tile Kernel Support

**Risk Level:** High
**Estimated Effort:** Full day
**Prerequisites:** Session 4 complete (all files updated, validated on RTX 5090)

---

## Objective

Upgrade the skill from CUDA 13.2 to CUDA 13.3. The primary feature is **Tile Kernels** — a new programming model where code operates on entire tile blocks rather than individual threads, with the compiler managing thread-level parallelism. This is additive (SIMT content remains valid) but requires new content across the programming guide, diagnosis playbook, analysis dimensions, and workflow.

## Background: What Are Tile Kernels?

Tile Kernels (`__tile_global__`, `cuda_tile.h` / `cuda.tile`) are an alternative to traditional SIMT CUDA:

| Aspect | SIMT (existing) | Tile (new) |
|---|---|---|
| Granularity | Individual threads | Entire blocks |
| Indexing | `blockIdx` + `threadIdx` | `ct::bid()` only |
| Parallelism | Explicit per-thread code | Compiler-managed |
| Memory access | Per-element loads/stores | Tile-level operations |
| Shared memory | Explicit `__shared__` | Compiler-optimized |
| Warp divergence | Programmer's concern | Not applicable |
| Language | C++ (`__global__`) | C++ (`__tile_global__`) and Python (`cuda.tile`) |

**Full API surface** (from official NVIDIA docs, all profiling-relevant):
- **Declarations**: `__tile_global__` (kernel entry), `__tile__` (device helper); no cross-calling with `__global__`/`__device__`
- **Launch**: `kernel<<<blocks, 1>>>(...)` — second chevron MUST be 1
- **Indexing**: `ct::bid()` (block index), `ct::num_blocks()` (grid size)
- **Tiles**: Fixed-size, power-of-two, compile-time shapes; `ct::zeros`, `ct::ones`, `ct::full`, `ct::iota`
- **Memory**: partition_view (structured, TMA-eligible) vs gather/scatter (irregular); `load_masked`/`store_masked` for boundary handling
- **Primitives**: `ct::mma()` (matmul-accumulate), reductions (`ct::sum/prod/max/min`), scans (`cumsum/cumprod`), transpose/permute, element-wise selection (`ct::select`)
- **Atomics**: `atomic_add`, `atomic_cas`, `atomic_xchng`, bitwise atomics — cross-block (device scope) and intra-block (block scope)
- **Broadcasting**: NumPy-style; scalar-tile, singleton expansion, trailing-dimension alignment
- **Optimization hints**: `cutile::hint(arch, kind=value)` — kinds: `num_cta_in_cga`, `occupancy`, `latency`, `allow_tma`; arch codes: 0=all, 900=sm_90, 1000=sm_100 (1200=sm_120 by pattern, unconfirmed)
- **Performance annotations** (critical for good ncu results): `__restrict__` on pointers, `ct::assume_aligned(ptr, 16_ic)` for TMA eligibility, `ct::irange()` for loop pipelining, partition_view preference over gather
- **Compile-time constants**: `_ic` literal suffix (e.g., `128_ic`), `ct::integral_constant`

**Constraints:** Power-of-two tile dimensions, compile-time shapes, no cross-calling between tile and SIMT functions, sm_80+ required (sm_90+ for TMA).

**Reference:** https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-tile-kernels.html

## Scope

### In Scope

1. **Version bump** — Update CUDA 13.2 → 13.3 references across all files.

2. **Programming guide expansion** — New section in `blackwell-cuda-programming.md`:
   - Tile kernel programming model on RTX 5090
   - When to use tiles vs SIMT (decision framework)
   - RTX 5090-specific constraints (sm_120, 100 KB shared/SM, TMA availability)
   - Performance guidelines for tile kernels (alignment, restrict, partition_view, irange)
   - Tile kernel profiling signals (how ncu metrics differ from SIMT)

3. **Diagnosis playbook** — New patterns for tile kernel performance issues:
   - Tile kernel occupancy (compiler-managed blocks vs manual warps)
   - Memory access efficiency (partition_view vs gather/scatter, TMA lowering)
   - MMA utilization (ct::mma vs manual tensor core usage)
   - Atomic contention (cross-block device-scope vs intra-block patterns)
   - Compiler optimization hints tuning (occupancy, latency, allow_tma)

4. **Analysis dimensions update** — Assess which of the 6 dimensions apply to tile kernels:
   - Occupancy: different model (no threadIdx, compiler manages warps)
   - Stalls: no warp divergence, different stall signatures
   - Tensor core: ct::mma vs smsp pipe metrics
   - Memory: tile-level coalescing handled by compiler

5. **Workflow update** — Phase 2 variant for tile kernel harness:
   - `__tile_global__` compilation (`cuda_tile.h` include)
   - ncu collection for tile kernels (same flags? different sections?)

6. **Hardware validation** — Profile a tile kernel on RTX 5090:
   - Confirm sm_120 supports tile kernels
   - Compare ncu metric output between SIMT and tile versions of the same kernel
   - Identify which metrics are meaningful for tile kernels
   - Validate TMA availability on sm_120

7. **Performance annotations** — Document the critical tile-kernel performance annotations and their profiling implications:
   - `__restrict__` pointers (enables read/write interleaving)
   - `ct::assume_aligned(ptr, 16_ic)` (enables TMA lowering)
   - `ct::irange()` (enables compiler loop pipelining/vectorization)
   - Partition_view preference over gather (structured → TMA path)

8. **Common issues update** — Tile kernel gotchas:
   - Launch syntax (second chevron must be 1)
   - No cross-calling between tile and SIMT functions
   - Compile-time constant requirements (`_ic` literals, `Constant[T]`)

9. **SKILL.md update** — Mention tile kernel support in skill description

### Out of Scope

- Python `cuda.tile` programming guide (the skill focuses on C++ CUDA and ncu profiling)
- Rewriting existing SIMT content (tile kernels are additive)
- Tile kernel autotuning framework (optimization hints are documented, not automated)
- Performance benchmarking of tile vs SIMT (the skill profiles, it doesn't benchmark)

## Key Unknowns (Require Hardware Validation)

| Unknown | Validation Method | Risk |
|---|---|---|
| sm_120 tile kernel support | Compile and run a `__tile_global__` kernel | Low — sm_120 > sm_80 requirement |
| TMA availability on sm_120 | Check `allow_tma` hint behavior | Medium — TMA may be sm_90+ only |
| ncu metric behavior for tile kernels | Profile tile kernel, compare to SIMT | High — metrics may be meaningless or different |
| Occupancy model for tile kernels | Check `sm__warps_active` on tile kernel | Medium — compiler manages warps |
| Stall signatures for tile kernels | Check pcsamp stall distribution | Medium — no warp divergence expected |
| Hint architecture code for sm_120 | Test `cutile::hint(1200, ...)` | Low — pattern suggests 1200, but unconfirmed |

## Files Modified

| File | Action | Description |
|---|---|---|
| `blackwell-cuda-programming.md` | Modify | Version bump + tile kernel programming section |
| `reference/01-workflow.md` | Modify | Tile kernel harness/collection variant |
| `reference/05-analysis-dimensions.md` | Modify | Tile kernel dimension applicability |
| `reference/06-diagnosis-playbook.md` | Modify | Tile kernel diagnosis patterns |
| `reference/08-rtx5090-metric-names.md` | Modify | Tile kernel metric validation notes |
| `reference/09-common-issues.md` | Modify | Tile kernel gotchas |
| `README.md` | Modify | Version bump |
| `reference/04-python-api.md` | Modify | Version bump in paths |
| `helpers/harness_template.cu` | Possibly modify | Tile kernel harness variant |
| `SKILL.md` | Modify | Mention tile kernel support in skill description |
| `docs/project_contract.md` | Modify | Version bump CUDA 13.2→13.3, add session 5 |

## Exit Criteria

| ID | Check | Method |
|---|---|---|
| E5-1 | Zero references to CUDA 13.2 outside docs/ | grep |
| E5-2 | Tile kernel compiles and runs on RTX 5090 | nvcc -arch=sm_120 with cuda_tile.h |
| E5-3 | Tile kernel section exists in programming guide | grep for "Tile Kernel" |
| E5-4 | At least 2 tile-kernel-specific diagnosis patterns | grep in playbook |
| E5-5 | ncu metrics validated for tile kernels | Hardware validation run |
| E5-6 | When-to-use decision framework exists | Section in programming guide |
| E5-7 | At least 1 atomic contention diagnosis pattern | grep in playbook |
| E5-8 | Performance annotations documented with profiling implications | grep in programming guide |
| E5-9 | SKILL.md mentions tile kernels | grep |

## References

- CUDA Programming Guide: Tile Kernels — https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-tile-kernels.html
- PRD §5 Toolchain Requirements — version requirements
- Evidence Map §4 — metric validation methodology
