# Session 3 Tasks

## 1. Hardware Validation Setup

- [ ] 1.1 Verify ncu_report import path (G-6)
- [ ] 1.2 Write temp vector_add kernel to /tmp and compile with sm_120
- [ ] 1.3 Collect ncu report with `--set full --section PmSampling`
- [ ] 1.4 Extract full metric list via `action.metric_names()` to /tmp/sm120_metrics.txt

## 2. Metric Validation (G-2)

- [ ] 2.1 Extract current B200_KEY_METRICS list from ncu_utils.py
- [ ] 2.2 Diff B200 metrics against sm_120 metric list (categorize: present/removed/new)
- [ ] 2.3 Verify stall metrics (STALL_METRICS from extract_stall_hotspots.py) against sm_120
- [ ] 2.4 Verify PM sampling metrics (DEFAULT_METRICS from plot_timeline.py) against sm_120
- [ ] 2.5 Check validation threshold (>=80% present) — escalate if below

## 3. Gap Experiments (G-1, G-5, G-8)

- [ ] 3.1 G-1: Test max dynamic shared memory per block via cudaFuncSetAttribute
- [ ] 3.2 G-5: Search metric list for TMEM-related metrics
- [ ] 3.3 G-8: Test shared memory carveout options via cudaFuncSetCacheConfig

## 4. Update ncu_utils.py

- [ ] 4.1 Rename B200_KEY_METRICS → RTX5090_KEY_METRICS
- [ ] 4.2 Replace metric list content with validated sm_120 metrics
- [ ] 4.3 Update _locate_ncu_report() to handle package directories
- [ ] 4.4 Update docstring and comments (remove B200/sm_100 references)

## 5. Update analyze_reports.py

- [ ] 5.1 Update import from B200_KEY_METRICS to RTX5090_KEY_METRICS
- [ ] 5.2 Add RTX 5090 peak throughput constants (bandwidth ~1792 GB/s)
- [ ] 5.3 Update docstring and comments (remove B200 references)

## 6. Update extract_stall_hotspots.py

- [ ] 6.1 Update STALL_METRICS with validated metric names
- [ ] 6.2 Remove any B200-specific references (if any)

## 7. Update plot_timeline.py

- [ ] 7.1 Update DEFAULT_METRICS with validated metric names
- [ ] 7.2 Remove any B200-specific references (if any)

## 8. Update harness_template.cu

- [ ] 8.1 Change compile target from compute_100/sm_100 to compute_120/sm_120
- [ ] 8.2 Update any B200-specific comments or constants

## 9. Update helpers/README.md

- [ ] 9.1 Update compile example from sm_100 to sm_120
- [ ] 9.2 Update B200_KEY_METRICS reference to RTX5090_KEY_METRICS
- [ ] 9.3 Update ncu_report PYTHONPATH example

## 10. Fix Stale Filename References

- [ ] 10.1 Update SKILL.md: 08-b200-metric-names.md → 08-rtx5090-metric-names.md
- [ ] 10.2 Update README.md: 08-b200-metric-names.md → 08-rtx5090-metric-names.md

## 11. Final Verification

- [ ] 11.1 Run all deterministic checks from session contract
- [ ] 11.2 Document gap resolution results
- [ ] 11.3 Verify done condition
