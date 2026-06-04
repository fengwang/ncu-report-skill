# Session 2 Brainstorming

## Context

Session 2 updates all 10 reference documents in `reference/` from B200/sm_100 to RTX 5090/sm_120. Session 1 already updated SKILL.md, blackwell-cuda-programming.md, and README.md.

## Key Decisions

| # | Question | Decision | Alternatives Considered |
|---|----------|----------|------------------------|
| 1 | New LLM pattern IDs | Append as O, P, Q | Replace I/J/K (renumbering chaos), Separate LLM section (different naming convention) |
| 2 | DC-only ISA in fix directions (tcgen05/wgmma/TMEM) | Replace with sm_120-available ISA (cp.async, mma.sync/WMMA) | Remove entirely (loses education), Keep annotated (clutters with inapplicable advice) |
| 3 | Framework kernel profiling guidance placement | New Phase 2.5 in workflow doc | Expand Phase 2 (less visible), Appendix (less discoverable) |
| 4 | Stale cross-references ("Blackwell principle N") | Update to match Session 1's named section headings | Remove entirely, Defer to Session 3 |

## Cross-Reference Mapping (old → new)

Session 1 restructured `blackwell-cuda-programming.md` from numbered principles to named sections under "Guideline Details":

| Old Reference | New Section Heading |
|---|---|
| Principle 1 | Ensure Sufficient Parallelism (Occupancy & Wave Count) |
| Principle 2 | Coalesce Memory Accesses |
| Principle 4 | Avoid Shared Memory Bank Conflicts |
| Principle 5 | Avoid Warp Divergence |
| Principle 6 | Control Register Pressure |
| Principle 7 | Hide Memory Latency (ILP and TLP) |
| Principle 8 | Use Appropriate Math Precision |
| Principle 10 | Use Tensor Cores Effectively |
| Principle 11 | Optimize Grid/Block Configuration |
| Principle 12 | Reduce Atomic Contention |
| Principle 13 | Vectorize Memory Access |
| Principle 15 | Pipeline Compute and Memory Access |
| Principle 16 | Reduce Synchronization Overhead |

## LLM Pattern Design

| Pattern | Signal | Cause | Fix |
|---------|--------|-------|-----|
| O — Decode bandwidth ceiling | `dram__bytes_read.sum.pct_of_peak_sustained_elapsed` > 80%, small grid, batch=1 decode | Single-token decode at ~1.8 TB/s is deeply memory-bound | Quantize weights/KV (FP8/FP4), speculative decoding, batching |
| P — KV-cache thrashing | `lts__t_sector_hit_rate.pct` very low, DRAM reads >> expected from weights alone | KV-cache exceeds 96 MB L2 → every attention pass reloads from DRAM | Quantize KV-cache (FP8/INT8), persistent L2 partitioning (up to 60 MB), reduce context length |
| Q — Quantization mismatch | Tensor core active but on higher-precision sub-pipe than needed | Kernel uses FP16 when FP8/FP4 tensor cores are available | Re-quantize model, use framework FP8 mode, check per-precision roofline breakpoints |

## Work Classification

- **Minor updates** (simple replacements): 00, 02, 03, 04
- **Moderate updates** (additive content): 01, 07, 09
- **Major rewrites** (recalibration + new content): 05, 06, 08
