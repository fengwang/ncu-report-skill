# Session 3: Helpers & Code Adaptation

**Risk Level:** High
**Estimated Effort:** Half-day
**Prerequisites:** Session 1 and Session 2 complete (specs and reference docs updated)

---

## Objective

Update all Python helper scripts and the CUDA harness template to target RTX 5090 (sm_120). Validate the metric name list against actual ncu output on the local 5090. Resolve evidence map gaps G-1, G-2, G-5, G-6, and G-8.

This is the highest-risk session because metric name compatibility between sm_100 and sm_120 is unverified (see `docs/evidence_map.md` §4). Incorrect metric names will cause silent failures in analysis scripts.

## Scope

### In Scope

1. **helpers/ncu_utils.py** — Major update:
   - Rename `B200_KEY_METRICS` → `RTX5090_KEY_METRICS` (or `SM120_KEY_METRICS`)
   - Validate every metric name by collecting an ncu report on the local 5090 and comparing against `action.metric_names()`
   - Remove metrics that don't exist on sm_120
   - Add any new sm_120-specific metrics discovered
   - Annotate metrics with verification status (verified / carried-forward-unverified)
   - Update any hardcoded thresholds or constants that reference B200 specs
   - Verify `load_report()` / `load_action()` work with ncu 2026.2 report format

2. **helpers/analyze_reports.py** — Update:
   - Replace any hardcoded B200 metric names
   - Update peak throughput constants for RTX 5090 (used in efficiency % calculations)
   - Update bandwidth ceiling (8 TB/s → 1.792 TB/s)
   - Test by running against a real ncu report from the local 5090

3. **helpers/extract_stall_hotspots.py** — Update:
   - Verify stall reason metric names exist on sm_120
   - Update any B200-specific stall categorization

4. **helpers/plot_timeline.py** — Update:
   - Verify PM sampling metric names on sm_120
   - Update any B200-specific timeline interpretation constants

5. **helpers/harness_template.cu** — Update:
   - Compile target → sm_120 in all comments and example commands
   - Verify template compiles and runs on local 5090: `nvcc -arch=sm_120 -lineinfo`
   - Update default block/grid size suggestions to match RTX 5090 occupancy sweet spots

6. **Metric validation procedure** (core of this session):
   - Compile a simple kernel (e.g., vector add or SGEMM) targeting sm_120
   - Collect an ncu report with `--set full`
   - Extract the full list of available metrics via `action.metric_names()`
   - Diff against the current B200 metric list
   - Categorize: {present on both, renamed, removed, new on sm_120}
   - Update the curated metric list accordingly

7. **Gap resolution:**
   - **G-1**: Test `cudaFuncSetAttribute(kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, N)` with increasing N to find the opt-in max shared memory per block
   - **G-2**: Full metric name validation (see item 6)
   - **G-5**: Profile a tensor-core kernel and check for TMEM-related metrics
   - **G-6**: Locate and verify the `ncu_report` Python module import path
   - **G-8**: Test shared memory carveout options via `cudaFuncSetCacheConfig`

### Out of Scope

- Modifying reference documentation (Session 2)
- Adding new LLM-specific helper scripts (only update existing ones)
- End-to-end workflow testing (Session 4)
- `helpers/safetensors_loader.h` — GPU-independent header-only library, no changes needed
- `helpers/list_flashinfer_workloads.py` — Dataset browsing utility, no GPU-specific logic

## Files Modified

| File | Action | Description |
|---|---|---|
| `helpers/ncu_utils.py` | Major rewrite | Metric list rename + validation, threshold updates |
| `helpers/analyze_reports.py` | Modify | Metric names, throughput constants, bandwidth ceiling |
| `helpers/extract_stall_hotspots.py` | Modify | Stall metric name verification |
| `helpers/plot_timeline.py` | Modify | PM sampling metric verification |
| `helpers/harness_template.cu` | Modify | Compile target, default launch config |

## Validation Procedure

The metric validation is the critical path of this session. Detailed steps:

```
Step 1: Compile a test kernel
  nvcc -arch=sm_120 -lineinfo -o /tmp/test_kernel helpers/harness_template.cu

Step 2: Collect a full ncu report
  ncu --set full --section PmSampling -o /tmp/test_report /tmp/test_kernel

Step 3: Extract metric names
  python3 -c "
  import sys; sys.path.insert(0, '<ncu_report_path>')
  import ncu_report
  report = ncu_report.load_report('/tmp/test_report.ncu-rep')
  action = report[0]  # first kernel
  names = sorted(action.metric_names())
  with open('/tmp/sm120_metrics.txt', 'w') as f:
      for n in names: f.write(n + '\n')
  print(f'Total metrics: {len(names)}')
  "

Step 4: Diff against current B200 list
  Extract B200_KEY_METRICS from ncu_utils.py, diff with sm120_metrics.txt.

Step 5: Update ncu_utils.py with validated metric names.
```

## Deliverables

1. `helpers/ncu_utils.py` with renamed and validated metric list.
2. All helper scripts updated with sm_120 metric names and RTX 5090 constants.
3. `helpers/harness_template.cu` compiling and running on local 5090.
4. Gap resolution report:
   - G-1: Max dynamic shared memory per block on RTX 5090
   - G-2: Full metric diff (added/removed/renamed between sm_100 and sm_120)
   - G-5: TMEM metric availability
   - G-6: Verified ncu_report import path
   - G-8: Shared memory carveout options

## Exit Criteria

| ID | Check | Method |
|---|---|---|
| E3-1 | No `B200` references in helpers/ | `grep -ri "B200\|b200" helpers/` returns empty |
| E3-2 | Metric list renamed | `grep "B200_KEY_METRICS" helpers/ncu_utils.py` returns empty |
| E3-3 | Harness compiles on sm_120 | `nvcc -arch=sm_120 -lineinfo helpers/harness_template.cu -o /tmp/test` succeeds |
| E3-4 | Metric list validated | At least 80% of metrics in the curated list confirmed present on sm_120 via `action.metric_names()` |
| E3-5 | ncu_report imports successfully | `python3 -c "import ncu_report"` succeeds with correct sys.path |
| E3-6 | Bandwidth constant updated | `grep "1.792\|1792\|1.8" helpers/analyze_reports.py` finds the RTX 5090 bandwidth value |
| E3-7 | Gap G-1 resolved | Max shared memory per block documented (48 KB default, opt-in max = ?) |

## Risk Mitigation

- **Metric name breakage**: If >20% of B200 metrics are missing on sm_120, escalate to a dedicated metric discovery sub-task before updating analysis scripts.
- **Harness compilation failure**: If sm_120 target fails with CUDA 13.2, check if a toolkit update is needed. Fallback: use `compute_120` with JIT compilation.
- **ncu_report API changes**: If the Python API signature changed in ncu 2026.2, update `load_report()` / `load_action()` wrappers first.

## References

- `docs/evidence_map.md` §4 — Metric compatibility evidence and gaps
- `docs/evidence_map.md` Gaps G-1, G-2, G-5, G-6, G-8 — Specific validation targets
- `docs/prd.md` §4.3 — Throughput figures for constant updates
- `docs/prd.md` §5 — Toolchain versions
