# Session 2 Implementation Plan

## Task 1: Metric Names File Migration

### 1.1 Rename file
```bash
git mv reference/08-b200-metric-names.md reference/08-rtx5090-metric-names.md
```

### 1.2-1.4 Update content
- Replace title "B200 (sm_100)" → "RTX 5090 (sm_120)"
- Replace all "B200" → "RTX 5090", "sm_100" → "sm_120" throughout
- Replace "Nsight Compute 2026.1" → "Nsight Compute 2026.2"
- Add header note: metrics carried forward from sm_100, validation pending Session 3
- Add per-group annotation: "Carried forward from sm_100. Validation on sm_120 pending Session 3."
- Update discovery commands: `--chip gb202` (note: RTX 5090 die)
- Update "B200 = GB202" comment to "RTX 5090 = GB202"

### 1.5 Verify
```bash
grep -ri 'B200\|sm_100\|b200' reference/08-rtx5090-metric-names.md
# Must return empty
```

---

## Task 2: Analysis Dimensions Recalibration

### 2.1 Dimension 1 — Occupancy
In `reference/05-analysis-dimensions.md`:
- Line with `(148 on B200)` → `(170 on RTX 5090)`
- "B200 with 148 SMs" → "RTX 5090 with 170 SMs"
- "if `launch__grid_size < 148 × blocks_per_SM`" → "< 170 × blocks_per_SM"
- Header "(B200 / sm_100 names)" → "(RTX 5090 / sm_120 names)"

### 2.2 Dimension 2 — PM sampling note
- No B200-specific text in current Dimension 2 (verify during implementation)

### 2.3 Dimension 4 — Tensor cores
- Replace "B200 uses 5th-gen tensor cores with `tcgen05.mma` + TMEM accumulators" → "RTX 5090 uses 5th-gen tensor cores accessed via `mma.sync` PTX or the WMMA C++ API"
- Remove tcgen05 PTX sequence (tcgen05.alloc, tcgen05.mma, tcgen05.ld, tcgen05.dealloc)
- Replace "CUTLASS 4.x" recommendation → keep (still valid for sm_120)
- Update "50%+ on B200" → "50%+ on RTX 5090"

### 2.4 Dimension 5
- "~2µs interval on B200" → "~2µs interval on RTX 5090"

### 2.5 Dimension 6
- No explicit bandwidth value in current Dim 6 text (bandwidth is relative/percentage-based)
- Verify no B200-specific references

### 2.6 Global sweep
- Search for any remaining "B200", "sm_100", "sm100" — replace all

### 2.7 Verify
```bash
grep -ri 'B200\|sm_100\|b200' reference/05-analysis-dimensions.md  # must be empty
grep -c '170' reference/05-analysis-dimensions.md                    # must be > 0
grep -c '48 warps\|48 warp' reference/05-analysis-dimensions.md     # must be > 0
grep -c '24 blocks\|24 block' reference/05-analysis-dimensions.md   # must be > 0
```

---

## Task 3: Diagnosis Playbook Recalibration + LLM Patterns

### 3.1-3.6 Recalibrate existing patterns
- Pattern A: "148-SM B200" → "170-SM RTX 5090", example "64 blocks on a 148-SM B200" → "64 blocks on a 170-SM RTX 5090"
- Pattern B: SM count references (verify — may not have explicit count)
- Pattern C: Add note about GDDR7 bandwidth impact
- Pattern E: Replace "tcgen05.cp (Blackwell)" with "cp.async (Ampere+)" in fix list; remove Blackwell-specific reference
- Pattern F: Replace "B200, tensor cores can do 16× the FMA throughput" with RTX 5090 ratio (BF16 tensor 209.5 TFLOPS / FP32 104.8 TFLOPS = 2× for BF16→FP32); replace "tcgen05.mma (Blackwell)" with "mma.sync / WMMA"; remove "TMEM (Blackwell)"

### 3.7 Cross-reference updates
| Old | New |
|---|---|
| "Blackwell principle 1" | "See `blackwell-cuda-programming.md` § Ensure Sufficient Parallelism" |
| "Blackwell principles 2, 13" | "See `blackwell-cuda-programming.md` § Coalesce Memory Accesses, § Vectorize Memory Access" |
| "Blackwell principle 4" | "See `blackwell-cuda-programming.md` § Avoid Shared Memory Bank Conflicts" |
| "Blackwell principle 5" | "See `blackwell-cuda-programming.md` § Avoid Warp Divergence" |
| "Blackwell principle 6" | "See `blackwell-cuda-programming.md` § Control Register Pressure" |
| "Blackwell principles 7, 15" | "See `blackwell-cuda-programming.md` § Hide Memory Latency, § Pipeline Compute and Memory Access" |
| "Blackwell principle 8" | "See `blackwell-cuda-programming.md` § Use Appropriate Math Precision" |
| "Blackwell principle 10" | "See `blackwell-cuda-programming.md` § Use Tensor Cores Effectively" |
| "Blackwell principle 11" | "See `blackwell-cuda-programming.md` § Optimize Grid/Block Configuration" |
| "Blackwell principle 12" | "See `blackwell-cuda-programming.md` § Reduce Atomic Contention" |
| "Blackwell principle 15" | "See `blackwell-cuda-programming.md` § Pipeline Compute and Memory Access" |
| "Blackwell principle 16" | "See `blackwell-cuda-programming.md` § Reduce Synchronization Overhead" |

### 3.8 Pattern O — Decode bandwidth ceiling
Add after Pattern N (warp divergence), before the ranking template.

### 3.9 Pattern P — KV-cache thrashing
Add after Pattern O.

### 3.10 Pattern Q — Quantization mismatch
Add after Pattern P.

### 3.11-3.12 Verify
```bash
grep -ri 'B200\|sm_100\|b200' reference/06-diagnosis-playbook.md  # must be empty
grep -c 'Pattern O\|Pattern P\|Pattern Q' reference/06-diagnosis-playbook.md  # must be >= 3
```

---

## Task 4: Minor Reference File Updates

### 4.1-4.5 Simple replacements
Each file: find B200/sm_100 occurrences, replace with RTX 5090/sm_120 equivalents.

Specific changes:
- **00**: `compute_100,code=sm_100` → `compute_120,code=sm_120`; `flash_attn_b200_h128_baseline` → `flash_attn_rtx5090_h128_baseline`
- **02**: `compute_100,code=sm_100` → `compute_120,code=sm_120` (2 occurrences)
- **03**: "B200, ncu 2026.1" → "RTX 5090, ncu 2026.2"
- **04**: `nsight-compute-2026.1.0` → `nsight-compute-2026.2.0`; `08-b200-metric-names.md` → `08-rtx5090-metric-names.md` (3 links)
- **07**: "NVIDIA B200 (148 SM, CC 10.0)" → "NVIDIA RTX 5090 (170 SM, CC 12.0)"; compile flags sm_100→sm_120

### 4.6 Verify
```bash
grep -ri 'B200\|sm_100\|b200' reference/00-directory-layout.md reference/02-harness-guide.md reference/03-collection.md reference/04-python-api.md reference/07-report-template.md
# Must return empty
```

---

## Task 5: Workflow — Framework Profiling Guidance

### 5.1 Add Phase 2.5
Insert new section in `reference/01-workflow.md` between Phase 2 and Phase 3.

Content structure:
- "Phase 2.5 — Framework kernel identification (when source is unavailable)"
- When to use: TensorRT-LLM, vLLM, PyTorch compiled kernels
- Kernel identification: `nsys profile`, `cuobjdump --dump-function-names`
- Profile without source: `--set full` only (skip `--set source`)
- What you lose: per-line stall attribution, source view
- What you keep: aggregate metrics, SOL, occupancy, stalls, DRAM throughput
- Framework-specific tips: Triton JIT naming, TRT fused kernel naming

### 5.2 Verify
```bash
grep -c 'Phase 2.5\|framework' reference/01-workflow.md  # must be > 0
```

---

## Task 6: Common Issues — Consumer GPU Section

### 6.1-6.3 Updates
- Replace "B200" → "RTX 5090" in SM throughput interpretation
- Replace "50%+ on B200" → "50%+ on RTX 5090"
- Update `08-b200-metric-names.md` reference → `08-rtx5090-metric-names.md`
- Update ncu_report path version
- Add new section "## Consumer GPU-specific issues"

### 6.4 Verify
```bash
grep -ri 'B200\|sm_100\|b200' reference/09-common-issues.md  # must be empty
```

---

## Task 7: Final Verification

Run all session contract deterministic checks:
```bash
grep -rci 'sm_100\|B200\|b200' reference/ | grep -v ':0$'       # must be empty
grep -c '170' reference/06-diagnosis-playbook.md                   # must be > 0
grep -c '48 warps\|48 warp' reference/05-analysis-dimensions.md   # must be > 0
grep -c '24 blocks\|24 block' reference/05-analysis-dimensions.md # must be > 0
test -f reference/08-rtx5090-metric-names.md                       # must pass
test ! -f reference/08-b200-metric-names.md                        # must pass
grep -c 'Pattern O\|Pattern P\|Pattern Q' reference/06-diagnosis-playbook.md  # >= 3
```
