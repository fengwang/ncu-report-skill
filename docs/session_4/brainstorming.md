# Session 4 Brainstorming: LLM Content & End-to-End Validation

**Date:** 2026-06-04
**Status:** Approved

---

## Context

Sessions 1–3 replaced all B200/sm_100 targeting with RTX 5090/sm_120. Session 3 validated 93/100 curated metrics on real hardware, discovering that 7 DRAM metrics were renamed (`dram__bytes_read` → `dram__bytes_op_read`) and PM sampling metrics are entirely different on sm_120. The helpers are correct, but 22 occurrences of old DRAM names persist across 9 reference/content files.

Session 4 completes the adaptation: finalize LLM content, fix stale metric names, resolve remaining evidence gaps, and validate the entire skill end-to-end on real hardware.

## Decisions

### D1: Blast Radius Expansion for DRAM Fix

**Chosen:** Expand `allowed_files` to include all DRAM-affected files (SKILL.md, reference/08, reference/04, reference/03, reference/07).
**Rejected:** Fix only contract-listed files (leaves stale names in user-facing docs); Session 3 amendment (adds process overhead for a mechanical fix).
**Reason:** The DRAM fix is a direct fix-forward from Session 3's validated metric names — contractually required and low-risk.

### D2: GPU Validation Approach

**Chosen:** Run GPU commands directly (environment has full toolchain access).
**Rejected:** User runs commands manually; script-only validation; skip hardware validation.
**Reason:** Full toolchain (nvidia-smi, nvcc, ncu, ncu_report) is accessible in this environment.

### D3: Task Ordering

**Chosen:** Content first, then validate.
**Rejected:** Validate first (tests broken state); interleave (complex coordination).
**Reason:** Validation should test the final state of the skill, not an intermediate state with known bugs.

### D4: G-7 Bandwidth Kernel

**Chosen:** Dedicated bandwidth kernel (device-to-device copy, float4, ≥256 MB buffers).
**Rejected:** Reuse vector_add (not a pure bandwidth test — 3 arrays, lower efficiency).
**Reason:** More accurate measurement of effective GDDR7 throughput under ncu profiling conditions.

### D5: Decode Checklist Depth

**Chosen:** Actionable checklist with ncu commands (~15-18 steps, each with metric/threshold/action).
**Rejected:** Concise decision tree (too shallow); combined tree+checklist (over-engineered).
**Reason:** Users need specific ncu metrics and RTX 5090 thresholds to act on, not abstract guidance.

### D6: Framework Coverage

**Chosen:** TensorRT-LLM + vLLM + PyTorch.
**Rejected:** TRT-LLM + vLLM only (misses PyTorch JIT scenario); generic guide (too abstract).
**Reason:** Covers all three major inference paths per PRD UC-2 and FR-7.

---

## Design

### Workstream A: DRAM & PM Sampling Metric Fix-Forward

Mechanical rename across all affected files. 7 DRAM metric patterns:

| Old (sm_100) | New (sm_120) |
|---|---|
| `dram__bytes_read` | `dram__bytes_op_read` |
| `dram__bytes_write` | `dram__bytes_op_write` |
| `dram__sectors_read` | `dram__sectors_op_read` |
| `dram__sectors_write` | `dram__sectors_op_write` |

All suffixes (`.sum`, `.pct_of_peak_sustained_elapsed`, `.per_second`) carry over unchanged.

**Files affected (22 occurrences across 10 files):**
SKILL.md, blackwell-cuda-programming.md, reference/01-workflow.md, reference/03-collection.md, reference/04-python-api.md, reference/05-analysis-dimensions.md, reference/06-diagnosis-playbook.md, reference/07-report-template.md, reference/08-rtx5090-metric-names.md, reference/09-common-issues.md.

**PM sampling fix:** Replace old stall-breakdown timeseries in reference/08 and reference/04 with sm_120 hardware-counter equivalents.

**Verification:** `grep -rn 'dram__bytes_read\|dram__bytes_write\|dram__sectors_read\|dram__sectors_write' --include='*.md' --include='*.py' --exclude-dir=docs .` returns zero matches (only `_op_` variants remain).

### Workstream B: LLM Content Finalization

#### B1: Precision-Specific Profiling Recipes

**Location:** `blackwell-cuda-programming.md`, new subsection after the decode signal table (after line ~321).

4 recipes (BF16/FP16, FP8, INT8, FP4), each with:
- When to use
- Tensor Core pipe metric to check
- Exact ncu collection command
- Key metrics with expected ranges
- Comparison baseline

Plus a cross-precision comparison recipe.

#### B2: Framework Profiling Walkthrough

**Location:** `reference/01-workflow.md`, expand Phase 2.5 (after line ~155).

3 new subsections:
1. **Framework-specific action mapping** — Table mapping ncu findings → framework config knobs for TRT-LLM, vLLM, PyTorch (~8-10 rows).
2. **RTX 5090 VRAM budget planning** — Model size estimation formula, KV-cache formula, example budgets for 7B/13B/70B at different precisions, OOM mitigation.
3. **Framework kernel naming cheat sheet** — Expanded kernel name patterns, how to identify kernel type from name.

#### B3: Decode Optimization Checklist

**Location:** `reference/06-diagnosis-playbook.md`, new section after Pattern Q (before "Ranking template").

~15-18 numbered steps in 3 phases:
- **Phase 1 — Characterize (Steps 1-5):** Confirm decode kernel, check DRAM BW, tensor core util, dominant stall, L2 hit rate.
- **Phase 2 — Optimize (Steps 6-13):** Address bottleneck — quantization, coalescing, KV-cache, occupancy, register spill, persistent L2, attention impl, warp divergence.
- **Phase 3 — Verify (Steps 14-16):** Re-profile, check regressions, document.

Each step: metric name, RTX 5090 threshold, FAIL action, PASS action. References existing patterns (O, P, Q) by name.

### Gap Resolutions

#### G-4: Cluster Launch Support

Test kernel using `cudaLaunchKernelEx` with cluster dims `{2,1,1}`. Document outcome (supported / rejected / unavailable) in `reference/09-common-issues.md`.

#### G-7: Effective GDDR7 Bandwidth

Dedicated memcpy kernel (float4 loads/stores, ≥256 MB buffers). Profile under ncu. Extract `dram__bytes_op_read.sum.per_second + dram__bytes_op_write.sum.per_second`. Compare vs 1.792 TB/s theoretical. Note throttling caveats. Document in `reference/09-common-issues.md`.

### Workstream C: End-to-End Validation

| Phase | Action | Success Criteria |
|---|---|---|
| 0 | Create `profile/validation_run/`, add to `.gitignore` | Directory exists, gitignored |
| 1 | Verify environment (nvidia-smi, nvcc, ncu, ncu_report) | All tools respond correctly |
| 2 | Build test kernel with `nvcc -arch=sm_120 -lineinfo` | Compiles without error |
| 3 | Collect two ncu reports (full + source sets) | Two `.ncu-rep` files produced |
| 4 | Run all 3 Python helpers against the reports | No metric-not-found errors, structured output |
| 5 | Apply six-dimension framework to parsed output | Each dimension produces meaningful values |
| 6 | Generate `profile/validation_run/REPORT.md` | Evidence-backed findings, not placeholders |

Cross-file consistency sweep runs last.
