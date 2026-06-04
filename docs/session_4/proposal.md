# Session 4 Proposal: LLM Content & End-to-End Validation

**Date:** 2026-06-04
**Source:** `docs/session_4/brainstorming.md`

---

## Motivation

Session 3 validated 93/100 curated metrics on real RTX 5090 hardware, discovering 7 DRAM metrics renamed on sm_120 and completely different PM sampling metrics. The helpers are corrected but 22 stale DRAM metric names persist in reference docs — users following these docs will get `None` values. Additionally, the LLM-specific content (precision recipes, framework walkthrough, decode checklist) exists in partial form and needs finalization. The full end-to-end workflow has never been validated on real hardware.

## Changes

### Fix-Forward
- Rename all old DRAM metric names (`dram__bytes_read` → `dram__bytes_op_read`, etc.) across 10 files
- Fix PM sampling metric names in reference/08 and reference/04

### LLM Content
- Add precision-specific profiling recipes (BF16, FP8, INT8, FP4) to programming guide
- Expand framework profiling walkthrough with action mapping, VRAM budget, kernel naming
- Add decode optimization checklist (~16 steps) to diagnosis playbook

### Gap Resolutions
- G-4: Test cluster launch support on RTX 5090, document result
- G-7: Measure effective GDDR7 bandwidth under ncu profiling

### Validation
- Run full 6-phase workflow on local RTX 5090
- Cross-file consistency sweep (B200/sm_100, hardware numbers, metric names)

## Capabilities

### New Capabilities
1. **precision-profiling-recipes** — Per-precision ncu collection and analysis recipes for BF16, FP8, INT8, FP4 on RTX 5090
2. **decode-optimization-checklist** — Actionable ~16-step checklist for single-user decode optimization with specific metrics and thresholds
3. **framework-action-mapping** — Table mapping ncu findings to framework configuration changes for TRT-LLM, vLLM, PyTorch
4. **vram-budget-planning** — Model size estimation and VRAM budget reference for RTX 5090's 32 GB
5. **cluster-launch-documentation** — G-4 resolution: cluster support status on consumer Blackwell
6. **effective-bandwidth-measurement** — G-7 resolution: measured GDDR7 bandwidth under profiling

### Modified Capabilities
7. **dram-metric-names** — All DRAM metric references updated from sm_100 to sm_120 naming across 10 files
8. **pm-sampling-metrics** — PM sampling metric list updated to sm_120 hardware-counter equivalents
9. **framework-kernel-identification** — Expanded kernel naming patterns for TRT-LLM, vLLM, PyTorch
10. **end-to-end-validation** — Full workflow validated on real RTX 5090 hardware with report artifact

## Impact

**Files modified:** SKILL.md, blackwell-cuda-programming.md, reference/01-workflow.md, reference/03-collection.md, reference/04-python-api.md, reference/05-analysis-dimensions.md, reference/06-diagnosis-playbook.md, reference/07-report-template.md, reference/08-rtx5090-metric-names.md, reference/09-common-issues.md, .gitignore

**Files created:** profile/validation_run/REPORT.md (gitignored, not committed)

**No new dependencies.** All content is self-contained markdown/prose.
