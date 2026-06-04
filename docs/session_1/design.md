# Session 1 Design — Core Specs & Programming Guide

**Date:** 2026-06-04

---

## Context

Three files need modification. `blackwell-cuda-programming.md` is a full rewrite (~730 → ~700 lines). `SKILL.md` and `README.md` are targeted edits. All B200 content is replaced; no backward compatibility is needed.

The programming guide currently contains four major sections that must be removed (tcgen05, TMEM, 2CTA, decompression engine) and three new sections added (GDDR7 memory strategy, sm_120 Tensor Core reality, LLM inference). The 16 core guidelines remain structurally intact but every hardware number changes.

## Goals

- Every hardware parameter in all three files matches PRD §4.1 verified specs.
- Zero references to B200, sm_100, or B200-specific values.
- Programming guide is self-consistent and accurately reflects sm_120 capabilities.
- LLM inference section exists with decode bandwidth analysis and precision roofline.
- tcgen05/TMEM/2CTA availability clearly documented as "not available on sm_120."

## Non-Goals

- Metric name validation (Session 3).
- Helper script modifications (Session 3).
- Reference doc updates (Session 2).
- End-to-end profiling validation (Session 4).

## Decisions

### D-1: Programming Guide Structure

**Choice:** Full restructure (Approach B).

**Rationale:** The original structure was organized around Blackwell data-center features (tcgen05, TMEM, 2CTA) as headline sections. Removing 3 of 4 headline sections while adding 3 new sections makes in-place editing produce an incoherent document. A clean rewrite with a new section ordering produces a more logical reading flow.

**Alternative considered:** Preserve structure, swap content (Approach A). Rejected because the resulting document would have the architecture-overview section immediately followed by guidelines, with no bridge material on the actual Tensor Core programming model.

### D-2: Tensor Core Section Approach

**Choice:** Document the actually-available ISA (mma.sync/WMMA) with a brief note explaining why tcgen05/wgmma are absent.

**Rationale:** Users will encounter mma.sync instructions in cuBLAS/CUTLASS-generated SASS. They need to understand what they're seeing in ncu reports. A brief "why not tcgen05" note prevents confusion for users who read NVIDIA's Blackwell architecture docs (which describe tcgen05 as "the" Blackwell TC ISA).

**Alternative considered:** Only recommend cuBLAS/CUTLASS (skip ISA documentation). Rejected because profiling requires understanding the instruction-level behavior.

### D-3: FP4 Documentation

**Choice:** Document FP4 as library-only (cuBLAS/CUTLASS) with explicit note that direct PTX mma.sync FP4 is not available on sm_120.

**Rationale:** The RTX 5090 hardware supports FP4 (marketing: 3,352 TOPS sparse), but the PTX ISA on sm_120 doesn't expose FP4 mma.sync. Libraries (cuBLAS, CUTLASS 4.x) access FP4 through internal code paths. Users need to know they can't hand-write FP4 kernels via inline PTX.

### D-4: LLM Inference Section Scope

**Choice:** Focus on profiling-relevant content, not general LLM optimization.

Content scope:
1. Why single-token decode is deeply memory-bandwidth-bound on RTX 5090 (~1.8 TB/s vs B200's 8 TB/s).
2. KV-cache memory budget within 32 GB VRAM (sizing formulas, context length limits per model size).
3. Precision-specific roofline breakpoints for decode (when each precision becomes compute-bound).
4. ncu signals that distinguish bandwidth-bound vs latency-bound vs compute-bound decode.
5. Quantization impact on decode throughput (FP4/FP8/INT8/BF16 bytes/token comparison).

Out of scope: framework configuration, model architecture choices, training.

### D-5: Guideline Number Substitution Strategy

**Choice:** Systematic pass with explicit mapping table.

Every B200 number in the 16 guidelines maps to an RTX 5090 equivalent:
- 148 SMs → 170 SMs
- 64 warps/SM → 48 warps/SM
- 32 blocks/SM → 24 blocks/SM
- 228 KB shared/SM → 100 KB shared/SM (99 KB opt-in)
- 227 KB shared/block → 99 KB shared/block opt-in (48 KB default)
- 8 TB/s bandwidth → ~1.8 TB/s bandwidth
- 126 MB L2 → 96 MB L2
- 192 GB HBM → 32 GB GDDR7
- sm_100a → sm_120a

After substitution, a full grep pass confirms no B200 values survive.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Missed B200 number in deep prose | Systematic grep for all B200-specific values (148, 228, 227, 64 warps, 32 blocks, 8 TB, 126 MB, 192 GB, HBM, sm_100) after writing |
| LLM section written too generically | Every claim references RTX 5090 bandwidth (~1.8 TB/s) or VRAM (32 GB) specifically |
| FP4 confusion | Explicit callout: "FP4 is NOT accessible via PTX mma.sync on sm_120" with evidence |
| Guideline NCU metric names may differ on sm_120 | Metric names are preserved as-is from B200 guide; Session 3 validates them. Add note: "Metric names assumed from sm_100; validation in progress." |

## Open Questions

None remaining. All hardware validation gaps (G-3, G-4, G-5) resolved during brainstorming. G-1 (shared memory opt-in) also resolved: 99 KB max.
