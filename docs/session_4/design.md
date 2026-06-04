# Session 4 Design: LLM Content & End-to-End Validation

**Date:** 2026-06-04
**Source:** `docs/session_4/brainstorming.md`, `docs/session_4/proposal.md`

---

## Context

The skill is 90% adapted to RTX 5090/sm_120 after Sessions 1-3. Two categories of work remain: (1) stale metric names in docs that will cause user-facing failures, and (2) LLM content that exists in partial form. The end-to-end workflow has never been run on real hardware.

The toolchain is live: RTX 5090 (CC 12.0), CUDA 13.2, ncu 2026.2, ncu_report Python module.

## Goals

- Every metric name in every file matches what sm_120 actually reports
- LLM content is RTX 5090-specific (not generic GPU advice)
- The full workflow provably works on real hardware

## Non-Goals

- Profiling real LLM frameworks (validation uses test kernels)
- Performance tuning the helper scripts
- Committing validation artifacts to git

## Decisions

### D1: Fix-forward before content

Fix DRAM/PM metric names first. This ensures the new content (precision recipes, decode checklist) uses correct metric names from the start, avoiding a second pass.

**Alternative considered:** Write content first with correct names, then fix old content. Rejected — two parallel naming conventions during writing increases error risk.

### D2: Precision recipes as inline subsections, not separate files

Add recipes directly to `blackwell-cuda-programming.md` after the existing decode signal table. The programming guide is the natural home — it already has the precision comparison table and the "Use Appropriate Math Precision" guideline.

**Alternative considered:** Separate `reference/10-precision-recipes.md`. Rejected — violates INV-1 (no new top-level files without justification) and fragments the precision narrative.

### D3: Decode checklist references existing patterns

The checklist says "see Pattern O" rather than duplicating Pattern O's content. This keeps the playbook DRY and avoids consistency drift.

**Alternative considered:** Self-contained checklist with all diagnosis details inline. Rejected — would duplicate 3 full patterns (~150 lines) and create a maintenance burden.

### D4: Validation kernel = harness_template vector_add

Use the existing harness template's vector_add for the main validation (Phases 2-6). It's a real user-facing template — validating it IS the test. The dedicated bandwidth kernel for G-7 is separate and ephemeral.

**Alternative considered:** Write a custom validation kernel. Rejected — the harness template is what users will actually compile; if it works, the skill works.

### D5: Gap test kernels are ephemeral

G-4 (cluster test) and G-7 (bandwidth test) kernels are written to `/tmp`, compiled, profiled, then results documented. They are not committed.

**Reason:** These are one-time hardware characterization experiments, not part of the skill's deliverables.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| ncu requires sudo for perf counters | Try without sudo first; document workaround in 09-common-issues.md if needed |
| Clock throttling distorts G-7 bandwidth measurement | Report both measured and theoretical; note gap as expected under profiling |
| PM sampling sections may not exist on sm_120 | Session 3 already confirmed different section names; use validated names |
| Framework action mapping may become stale | Keep recommendations generic to major version (TRT-LLM 0.x, vLLM 0.x); note version caveat |
| Validation kernel too simple to exercise all metric paths | Acknowledged by adversarial case list; the goal is workflow validation, not comprehensive metric coverage |

## Open Questions

None — all questions resolved during brainstorming.
