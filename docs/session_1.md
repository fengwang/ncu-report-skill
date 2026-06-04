# Session 1: Foundation — Core Specs & Programming Guide

**Risk Level:** Medium
**Estimated Effort:** Half-day
**Prerequisites:** None (first session)

---

## Objective

Replace all B200 hardware specifications with RTX 5090 verified specs across the skill's top-level files. Rewrite the Blackwell CUDA programming guide for consumer Blackwell (sm_120) constraints. After this session, the skill's "what GPU are we targeting" question is fully answered.

## Scope

### In Scope

1. **SKILL.md** — Replace B200 headline specs, hardware parameter table, and compile target references with RTX 5090 values. Update the skill description to reflect RTX 5090 targeting.

2. **blackwell-cuda-programming.md** — Full rewrite for RTX 5090 consumer Blackwell:
   - Replace the hardware parameter table (§ SM/cluster counts, memory hierarchy, etc.)
   - Rewrite shared memory guidance: 100 KB/SM ceiling, 48 KB/block default (not 228 KB/227 KB)
   - Rewrite memory bandwidth strategy: GDDR7 @ ~1.8 TB/s (not HBM3e @ 8 TB/s)
   - Remove NVLink and multi-GPU cluster content (RTX 5090 has no NVLink)
   - Remove dual-die / NV-HBI content (RTX 5090 is monolithic GB202)
   - Adjust occupancy guidance: 48 warps/SM, 24 blocks/SM (not 64/32)
   - Retain and verify: tcgen05 tensor core content (confirm applicability to sm_120)
   - Retain and verify: TMEM content (confirm availability on consumer Blackwell)
   - Add: GDDR7-specific considerations (if material differences from HBM exist)
   - Add: 32 GB VRAM constraint awareness
   - Add: LLM inference section — single-token decode as memory-bandwidth-bound regime, KV-cache sizing within 32 GB, quantization strategy (FP4/FP8/INT8/BF16) with roofline breakpoints per precision

3. **README.md** — Update to reference RTX 5090 instead of B200. Update toolchain requirements.

### Out of Scope

- Helper scripts (Session 3)
- Reference docs (Session 2)
- Metric name validation (Session 3)
- End-to-end validation (Session 4)

## Key Decisions to Make During Session

1. **tcgen05 on sm_120**: Attempt `nvcc -arch=sm_120` compilation of a tcgen05 PTX snippet. If it fails, the tensor core section must be rewritten for whatever ISA sm_120 uses.
2. **2CTA cluster mode**: Check if `cudaDeviceProp` reports cluster support on RTX 5090. If not, remove 2CTA content entirely.
3. **TMEM sections**: Determine if TMEM documentation applies to sm_120 or is data-center only. If uncertain, keep the content but flag it as "needs validation in Session 3."
4. **Shared memory carveout options**: Document the default (48 KB/block) and note that the opt-in max needs validation (Gap G-1).

## Files Modified

| File | Action | Description |
|---|---|---|
| `SKILL.md` | Modify | Replace all B200 specs with RTX 5090 specs |
| `blackwell-cuda-programming.md` | Major rewrite | Consumer Blackwell constraints + LLM content |
| `README.md` | Modify | Update GPU target, toolchain requirements |

## Deliverables

1. `SKILL.md` with RTX 5090 hardware specs, sm_120 compile target, updated description.
2. `blackwell-cuda-programming.md` rewritten for RTX 5090 with LLM inference section.
3. `README.md` updated.
4. Findings document (inline comments or notes) on tcgen05/TMEM/2CTA availability for sm_120.

## Exit Criteria

| ID | Check | Method |
|---|---|---|
| E1-1 | No B200/sm_100 references in modified files | `grep -i "sm_100\|B200" SKILL.md blackwell-cuda-programming.md README.md` returns empty |
| E1-2 | All hardware numbers match PRD §4.1 verified specs | Manual review of parameter tables |
| E1-3 | Compile target is sm_120 everywhere | `grep -i "sm_1" SKILL.md blackwell-cuda-programming.md README.md` shows only sm_120 |
| E1-4 | LLM inference section exists in programming guide | Section heading present with decode bandwidth analysis and precision roofline table |
| E1-5 | tcgen05/TMEM/2CTA availability documented | Each feature has a note stating "confirmed on sm_120" or "needs validation" |

## References

- `docs/prd.md` §4 — Verified hardware specifications
- `docs/evidence_map.md` §1–3 — Hardware evidence with confidence ratings
- `docs/evidence_map.md` Gaps G-3, G-4, G-5 — tcgen05, 2CTA, TMEM validation gaps
