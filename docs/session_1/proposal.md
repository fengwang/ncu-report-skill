# Session 1 Proposal — Core Specs & Programming Guide

**Date:** 2026-06-04

---

## Motivation

The existing skill targets B200 (sm_100) with hardware specs, Tensor Core ISA (tcgen05), and memory hierarchy (HBM3e @ 8 TB/s) that are fundamentally incompatible with RTX 5090 (sm_120). Live validation on the local GPU confirmed that sm_120 lacks tcgen05, wgmma, TMEM, and 2CTA — the four headline features of the B200 programming guide. Using the current guide on RTX 5090 produces incorrect occupancy calculations, wrong optimization recommendations, and references to unavailable hardware features.

## Agreed Changes

1. **Language switch**: Chinese → English across the programming guide.
2. **Hardware specs**: All B200 parameters replaced with RTX 5090 verified values (PRD §4.1).
3. **Compile target**: `sm_100a` → `sm_120a`.
4. **Tensor Core ISA**: tcgen05/wgmma sections removed. New section documents the actual ISA: `mma.sync` (Ampere/Ada era) and WMMA API.
5. **TMEM**: Section removed entirely (not accessible without tcgen05).
6. **2CTA / CTA Pair**: Section removed (cta_group not supported on sm_120).
7. **Decompression Engine**: Section removed (data-center feature).
8. **NVLink / DSMEM**: Content removed (RTX 5090 has no NVLink). Thread Block Clusters retained (confirmed available).
9. **Memory hierarchy**: HBM3e guidance replaced with GDDR7 @ ~1.8 TB/s strategy. Shared memory guidance updated for 100 KB/SM ceiling (99 KB opt-in max).
10. **Precision spectrum**: Updated for sm_120 reality — FP8 via mma.sync PTX, FP4 via libraries only.
11. **LLM inference**: New section covering decode bandwidth analysis, KV-cache within 32 GB, quantization strategy.
12. **16 core guidelines**: All RTX 5090 numbers, English prose.
13. **Guide structure**: Full restructure per Approach B from brainstorming.
14. **Comparison column**: Removed. RTX 5090 specs only.

## Capabilities

### New Capabilities

| ID | Capability | Description |
|---|---|---|
| N-1 | RTX 5090 Hardware Specs | Complete verified hardware parameter table for sm_120 |
| N-2 | sm_120 Architecture Overview | What's different from sm_100, what's NOT available |
| N-3 | GDDR7 Memory Strategy | Memory hierarchy guidance calibrated for ~1.8 TB/s GDDR7 |
| N-4 | sm_120 Tensor Core Guide | mma.sync/WMMA programming, cuBLAS/CUTLASS path |
| N-5 | Precision Roofline Table | FP4→FP64 breakpoints with sm_120 bandwidth |
| N-6 | LLM Inference Section | Decode bandwidth analysis, KV-cache sizing, quantization |

### Modified Capabilities

| ID | Capability | What Changes |
|---|---|---|
| M-1 | Core Guidelines (1–16) | All hardware numbers → RTX 5090; language → English |
| M-2 | Special Kernel Types | LLM decode attention updated for RTX 5090 bandwidth constraints |
| M-3 | Pre-Coding Checklist | Updated for sm_120a (remove tcgen05/TMEM/2CTA items, add mma.sync items) |
| M-4 | SKILL.md Frontmatter & Specs | B200 → RTX 5090 throughout |
| M-5 | README.md | GPU target, toolchain, description updated |

## Impact

- **blackwell-cuda-programming.md**: Full rewrite. ~730 lines current → estimated ~600-800 lines new (removed DC sections, added LLM/memory/TC sections).
- **SKILL.md**: ~15 targeted edits (frontmatter, description, hardware refs, compile target, metric file reference).
- **README.md**: ~10 targeted edits (description, requirements, toolchain versions).
- **No files outside blast radius affected.**
- **No dependencies introduced.**
