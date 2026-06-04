# Session 2 Design

## Context

10 reference files totaling ~104 KB need updating from B200/sm_100 to RTX 5090/sm_120. Three files need major rewrites (05, 06, 08); four need moderate updates (01, 07, 09, plus 08 rename); three need minor replacements (00, 02, 03, 04).

Session 1 already: restructured the programming guide with named sections (replacing numbered principles), confirmed sm_120 lacks tcgen05/wgmma/TMEM, documented mma.sync/WMMA as the available tensor core ISA.

## Goals

- Zero B200/sm_100 references remaining in `reference/`
- All numeric thresholds calibrated to RTX 5090 verified specs (PRD §4.1)
- Three LLM-specific diagnosis patterns with concrete ncu metric signals
- Framework kernel profiling guidance for opaque kernels

## Non-Goals

- Validating metric names on the actual GPU (Session 3)
- Updating helper Python scripts (Session 3)
- Running end-to-end profiling (Session 4)

## Decisions

### D-1: File processing order

Process in dependency order:
1. **08 (metric names)** first — rename file, establish the new name that other files reference
2. **05 (analysis dimensions)** — recalibrate the framework that the playbook references
3. **06 (diagnosis playbook)** — recalibrate patterns, add LLM patterns, depends on 05's values
4. **Minor files** (00, 02, 03, 04, 07) — simple replacements, can be parallelized
5. **01 (workflow)** — add Phase 2.5
6. **09 (common issues)** — add consumer GPU issues

**Why**: 08 must be renamed first because 04 and 09 link to it by filename. 05 must precede 06 because playbook patterns reference analysis dimension thresholds.

### D-2: Threshold recalibration strategy

For each threshold in the existing 8 patterns (A-H):
1. Identify the B200 value and its derivation
2. Derive the RTX 5090 equivalent using verified specs from PRD §4.1
3. Replace the value with the RTX 5090 equivalent

Key substitutions:
| Parameter | B200 | RTX 5090 | Used In |
|---|---|---|---|
| SM count | 148 | 170 | Patterns A, B (grid threshold) |
| Max warps/SM | 64 | 48 | Dim 1 (occupancy) |
| Max blocks/SM | 32 | 24 | Dim 1 (occupancy) |
| Shared mem/SM | 228 KB | 100 KB | Dim 1, Pattern H |
| DRAM bandwidth | 8 TB/s | ~1.8 TB/s | Dim 6, Patterns C, E, O |
| L2 cache | 126 MB | 96 MB | Pattern P |
| Persistent L2 | — | 60 MB | Pattern P |
| VRAM | 192 GB | 32 GB | Pattern P |

### D-3: LLM pattern design (O, P, Q)

Each pattern follows the existing pattern→cause→fix structure with:
- Concrete ncu metric signals (not generic prose)
- RTX 5090-specific thresholds (e.g., ~1.8 TB/s bandwidth ceiling, 96 MB L2)
- Cross-references to the programming guide's LLM Inference Profiling section

### D-4: Metric "unverified" flagging strategy

All metrics in 08-rtx5090-metric-names.md are carried forward from sm_100. Flag them as:
- Section header: note incremental validation approach
- Each metric group: annotated with "carried forward from sm_100, validation pending Session 3"
- Discovery commands updated: `--chip gb202` (the RTX 5090 die)

### D-5: Cross-reference update strategy

Replace all "Blackwell principle N" references with "See `blackwell-cuda-programming.md` § <Section Name>". Use the exact section heading from Session 1's restructured guide.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Incomplete threshold sweep (update A, forget E) | Systematic file walk-through, deterministic grep checks after each major file |
| Metric names invalid on sm_120 | Flag all as "unverified", Session 3 validates |
| LLM patterns too generic | Include specific ncu metric names and RTX 5090 thresholds |
| Cross-reference rot if guide restructures again | Use section headings (more stable than numbers) |

## Open Questions

None — all resolved in brainstorming.
