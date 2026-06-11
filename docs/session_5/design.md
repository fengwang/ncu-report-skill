# Session 5 Design — CUDA 13.3 Tile Kernel Support

## Context

The skill documents CUDA profiling on RTX 5090 (sm_120). Sessions 1–4 built the SIMT profiling framework. CUDA 13.3 adds tile kernels — a compiler-managed programming model where code operates on tile blocks, not individual threads. This session adds tile kernel support as additive content.

**Current state:** CUDA 13.2 references in 6 non-docs files. Zero tile kernel content. Hardware validation infrastructure from Session 4 (profile/validation_run/) is gitignored and reusable.

**Constraints:** Additive only (no SIMT changes). No new top-level files. Helper scripts stay stdlib-only. Content must be grounded in real ncu output, not hypothetical.

## Goals

- Users can profile tile kernels on RTX 5090 using the skill's workflow
- Diagnosis patterns are validated against real ncu output
- Decision framework helps users choose between SIMT and tile models
- All CUDA 13.2 references replaced with 13.3

## Non-Goals

- Python `cuda.tile` coverage (C++ and ncu profiling only)
- Tile kernel autotuning
- Benchmarking tile vs SIMT performance
- Rewriting SIMT content

## Decisions

### D1: Validation-First Task Ordering

**Choice:** Hardware validation before content writing.

**Why over content-first (Session 4 precedent):** Session 4 content was an evolution of known SIMT metrics. Tile kernel ncu behavior is completely unknown — the compiler manages warps, occupancy model differs, stall signatures may be unrecognizable. Writing content first risks cascading rewrites.

**Risk:** Validation could block if compilation or runtime fails. Mitigation: the version bump is independent and can proceed regardless. If tile compilation fails entirely, content falls back to documented architecture expectations with explicit "unvalidated" caveats.

### D2: Progressive 3-Kernel Validation

**Choice:** Three kernels of increasing complexity.

| Kernel | Purpose | Metrics Targeted |
|---|---|---|
| 1. Element-wise vector_add | Basic tile compilation, launch, metric sanity | Occupancy, stalls, memory bandwidth |
| 2. GEMM with ct::mma | Tensor core metrics under tile model | smsp pipe metrics, MMA utilization |
| 3. Reduction with atomics | Atomic contention under tile model | Atomic throughput, stall reasons |

**Why over single kernel:** Isolation. If mma metrics are wrong, we know it's not a compilation issue. If atomics stall differently, we know it's not an mma issue.

**Why over minimal+caveat:** The adversarial cases explicitly flag "trivial kernel that doesn't exercise mma, atomics, or multi-dimensional tile paths."

### D3: Tile Content Placement in Programming Guide

**Choice:** New top-level section `## Tile Kernel Programming Model (CUDA 13.3+)` placed after the existing "Special Kernel Types Quick Reference" section (~line 931) and before "Pre-Coding Checklist."

**Why not under Architecture Overview:** The tile kernel section needs its own decision framework, API reference, and performance guidelines. It's a programming model, not an architecture feature. Placing it as a peer section keeps it discoverable and self-contained.

**Subsections:**
1. What Are Tile Kernels (brief, link to NVIDIA docs)
2. When to Use Tiles vs SIMT (decision framework with ≥3 concrete factors)
3. RTX 5090 Constraints (sm_120, 100 KB shared/SM, TMA status)
4. API Quick Reference (declarations, launch, indexing, memory, primitives, atomics, hints)
5. Performance Annotations for Profiling (`__restrict__`, `assume_aligned`, `irange`, `partition_view`)
6. Profiling Tile Kernels (how ncu output differs from SIMT — grounded in validation data)

### D4: Diagnosis Pattern Structure

**Choice:** 4 new patterns following existing pattern→cause→fix structure, inserted as Pattern R through Pattern U after the existing Pattern Q.

| Pattern | Signal | Category |
|---|---|---|
| R: Tile kernel low occupancy | Compiler-managed warps < hardware max | Occupancy |
| S: Partition_view vs gather inefficiency | High global memory traffic despite tile-level access | Memory |
| T: Tile MMA underutilization | Low tensor core pipe activity in ct::mma kernel | Tensor core |
| U: Tile atomic contention | High atomic stall ratio in cross-block atomics | Atomics |

Each pattern references specific ncu metrics discovered during hardware validation. Patterns that cannot be grounded in real metrics get an explicit "expected signal — not hardware-validated" caveat.

### D5: Analysis Dimension Annotations (Not a New Dimension)

**Choice:** Add tile kernel annotations within each existing dimension, not a new Dimension 7.

**Why:** The session contract says "Assess which of the 6 dimensions apply to tile kernels." The dimensions are framework-level categories — occupancy, tail effect, stalls, tensor core, timeline, memory. Tile kernels are a programming model, not a new analysis category. Each dimension gets a "Tile kernel note" subsection explaining how the dimension's metrics behave differently under compiler-managed execution.

### D6: Harness Template Integration

**Choice:** Add a clearly marked tile kernel section to `harness_template.cu` after the existing SIMT kernel stub, using `#if 0` / `#endif` guards with a comment explaining how to enable.

**Why `#if 0` over `#ifdef`:** The template is a copy-paste starter. Users should see both models and uncomment the one they need. `#if 0` is simpler than defining a macro.

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| nvcc rejects `__tile_global__` on sm_120 | Low | Blocks all tile content | CUDA 13.3 docs say sm_80+; fall back to caveated content |
| ncu produces no useful metrics for tile kernels | Medium | Diagnosis patterns become hypothetical | Document what IS observed; caveat what isn't; patterns reference architecture docs |
| TMA not available on consumer sm_120 | Medium | TMA-related content needs caveats | Validate with `allow_tma` hint; document result either way |
| `cutile::hint(1200, ...)` rejected by compiler | Low | Hint documentation needs update | Test with 1200; if rejected, try 0 (all architectures); document finding |
| Warp-level metrics misleading for tile kernels | Medium | Occupancy analysis needs reframing | Validation kernel 1 will reveal this; adjust content accordingly |

## Open Questions

1. Does ncu's `--section` flag behave identically for tile kernels? (Resolved by validation)
2. Are PM sampling metrics available for tile kernels? (Resolved by validation)
3. What does the "active warps" metric mean when the compiler manages warps? (Resolved by validation)
