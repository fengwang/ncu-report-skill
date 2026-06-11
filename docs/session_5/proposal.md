# Session 5 Proposal — CUDA 13.3 Tile Kernel Support

## Motivation

CUDA 13.3 introduces **Tile Kernels** — a new programming model where code operates on entire tile blocks rather than individual threads, with the compiler managing thread-level parallelism (`__tile_global__`, `cuda_tile.h`). The skill currently targets CUDA 13.2 and documents only the SIMT programming model. Users profiling tile kernels on RTX 5090 need guidance on compilation, ncu collection, metric interpretation, and bottleneck diagnosis specific to this new execution model.

Source: Brainstorming decisions D1–D4. Session plan §Objective. PRD §5 toolchain requirements.

## Specific Changes

1. **Version bump** — Replace all CUDA 13.2 references with 13.3 across non-docs/ files (6 files, ~10 occurrences).
2. **Hardware validation** — Compile and profile 3 tile kernels of increasing complexity on RTX 5090 to determine which ncu metrics are meaningful, validate TMA availability, and confirm optimization hint architecture code for sm_120.
3. **Programming guide expansion** — New section in `blackwell-cuda-programming.md` covering tile kernel model, API surface, when-to-use decision framework, RTX 5090-specific constraints, and performance annotations with profiling implications.
4. **Diagnosis playbook expansion** — At least 4 new tile-kernel-specific patterns (occupancy, memory access, MMA utilization, atomic contention) grounded in hardware validation data.
5. **Analysis dimensions update** — Annotate each of the 6 dimensions with tile kernel applicability (occupancy model differs, stall signatures differ, tensor core via ct::mma, memory via partition_view/TMA).
6. **Workflow update** — Tile kernel harness/collection variant in Phase 2 (compilation with `cuda_tile.h`, launch syntax, ncu collection considerations).
7. **Common issues update** — Tile kernel gotchas: launch syntax (second chevron must be 1), cross-calling restriction, compile-time constant requirements.
8. **Harness template update** — Add tile kernel variant section to existing `harness_template.cu`.
9. **Metric names update** — Document which existing metrics are meaningful for tile kernels and any tile-specific metrics discovered during validation.
10. **SKILL.md update** — Mention tile kernel support as a supported programming model.
11. **Project contract amendment** — Update version to 1.1, CUDA 13.3, 5 sessions.

## Capabilities

### New Capabilities

| ID | Capability | Spec File |
|---|---|---|
| NC-1 | Version bump (CUDA 13.2 → 13.3) | `specs/version-bump.md` |
| NC-2 | Hardware validation (tile kernel compilation, profiling, metric analysis) | `specs/hardware-validation.md` |
| NC-3 | Tile kernel programming guide section | `specs/tile-programming-guide.md` |
| NC-4 | Tile kernel diagnosis patterns | `specs/tile-diagnosis-patterns.md` |
| NC-5 | Tile kernel analysis dimension annotations | `specs/tile-analysis-dimensions.md` |
| NC-6 | Tile kernel workflow variant | `specs/tile-workflow.md` |
| NC-7 | Tile kernel common issues | `specs/tile-common-issues.md` |
| NC-8 | Tile kernel harness template variant | `specs/tile-harness-template.md` |
| NC-9 | Tile kernel metric validation notes | `specs/tile-metric-notes.md` |

### Modified Capabilities

| ID | Capability | What Changes |
|---|---|---|
| MC-1 | SKILL.md skill description | Add tile kernel mention |
| MC-2 | Project contract | Version 1.1, CUDA 13.3, 5 sessions |

## Impact

- **Code:** `helpers/harness_template.cu` (tile variant section added)
- **Documentation:** 8 markdown files modified, all additive
- **Dependencies:** None added (cuda_tile.h is part of CUDA toolkit)
- **APIs:** None changed
- **Invariants preserved:** Six-dimension framework, pattern→cause→fix structure, SIMT content unchanged, no new top-level files
