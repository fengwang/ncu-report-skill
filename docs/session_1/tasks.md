# Session 1 Tasks

---

## 1. SKILL.md Updates

- [ ] 1.1 Update YAML frontmatter: description field to reference RTX 5090 / sm_120
- [ ] 1.2 Update title line and "Target hardware" line with RTX 5090 specs
- [ ] 1.3 Replace compile target references from sm_100/sm_100a to sm_120a
- [ ] 1.4 Update "Critical lessons" section: replace B200/sm_100 references
- [ ] 1.5 Update metric file reference (08-b200-metric-names.md → note it will be renamed in Session 2)
- [ ] 1.6 Run grep verification: zero B200/sm_100 matches in SKILL.md

## 2. Programming Guide — Front Matter & Architecture

- [ ] 2.1 Write new target platform section (RTX 5090 / sm_120a) with compile command
- [ ] 2.2 Write RTX 5090 hardware parameter table (single-column, from PRD §4.1)
- [ ] 2.3 Write Architecture Overview section (GB202 monolithic, sm_120 vs sm_100 differences)

## 3. Programming Guide — Memory Hierarchy

- [ ] 3.1 Write GDDR7 memory strategy section (~1.8 TB/s, effective bandwidth notes)
- [ ] 3.2 Document L2 cache (96 MB) and persistent L2 (60 MB) with usage guidance
- [ ] 3.3 Document shared memory hierarchy (100 KB/SM, 48 KB default, 99 KB opt-in, 1 KB reserved)

## 4. Programming Guide — Tensor Core & Precision

- [ ] 4.1 Write Tensor Core programming section (mma.sync/WMMA ISA, cuBLAS/CUTLASS path)
- [ ] 4.2 Write "why tcgen05/wgmma are absent" note
- [ ] 4.3 Write precision spectrum table (FP4→FP64 with throughput and roofline breakpoints)
- [ ] 4.4 Write FP4 library-only caveat
- [ ] 4.5 Write roofline interpretation guidance

## 5. Programming Guide — LLM Inference

- [ ] 5.1 Write decode bandwidth analysis (why decode is memory-bandwidth-bound on RTX 5090)
- [ ] 5.2 Write KV-cache sizing guidance (formula + worked example within 32 GB)
- [ ] 5.3 Write quantization strategy section (FP4/FP8/INT8/BF16 comparison)

## 6. Programming Guide — Core Guidelines

- [ ] 6.1 Write preamble section ("Why this document") in English
- [ ] 6.2 Write guideline overview table in English
- [ ] 6.3 Rewrite Guidelines 1–8 with RTX 5090 numbers, in English
- [ ] 6.4 Rewrite Guidelines 9–16 with RTX 5090 numbers, in English
- [ ] 6.5 Rewrite Special Kernel Types section with RTX 5090 constraints, in English
- [ ] 6.6 Rewrite Pre-Coding Checklist for sm_120a capabilities, in English

## 7. README.md Updates

- [ ] 7.1 Update description paragraph: B200 → RTX 5090
- [ ] 7.2 Update Requirements section: toolchain versions, sm_120
- [ ] 7.3 Update any inline references to B200/sm_100

## 8. Verification

- [ ] 8.1 Run deterministic grep checks from session contract
- [ ] 8.2 Verify hardware numbers match PRD §4.1 in all three files
- [ ] 8.3 Verify LLM section exists with decode analysis and precision roofline
- [ ] 8.4 Verify tcgen05/TMEM/2CTA status is documented
