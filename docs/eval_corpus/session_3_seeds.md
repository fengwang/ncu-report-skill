# Session 3 Eval Seeds

## Deterministic Checks

```bash
# E3-1: No B200 references in helpers/
grep -rci 'B200\|b200' helpers/ | grep -v ':0$'
# Expected: empty

# E3-2: Metric list renamed
grep -c 'B200_KEY_METRICS' helpers/ncu_utils.py
# Expected: 0

# E3-3: Harness compiles
nvcc -arch=sm_120 -lineinfo helpers/harness_template.cu -o /tmp/harness_test 2>&1; echo $?
# Expected: 0

# E3-4: ncu_report imports
python3 -c "import ncu_report; print('OK')"
# Expected: OK

# E3-5: Bandwidth constant
grep -c '1792' helpers/analyze_reports.py
# Expected: >= 1

# E3-6: DRAM metrics use sm_120 names
grep -c 'dram__bytes_op_read\|dram__bytes_op_write' helpers/ncu_utils.py
# Expected: >= 2

# E3-7: No stale filename references
grep '08-b200-metric-names' SKILL.md README.md
# Expected: empty

# E3-8: Metric list size
python3 -c "import sys; sys.path.insert(0, 'helpers'); from ncu_utils import RTX5090_KEY_METRICS; print(len(RTX5090_KEY_METRICS))"
# Expected: >= 100
```

## Regression Tests

```bash
# All sm_100 references gone from helpers
grep -rci 'sm_100\|sm100\|compute_100' helpers/ | grep -v ':0$'
# Expected: empty

# Stall metrics consistent between ncu_utils.py and extract_stall_hotspots.py
python3 -c "
import sys; sys.path.insert(0, 'helpers')
from ncu_utils import RTX5090_KEY_METRICS
pcsamp = [m for m in RTX5090_KEY_METRICS if 'pcsamp_warps_issue_stalled' in m]
print(f'pcsamp stall metrics in curated list: {len(pcsamp)}')
assert len(pcsamp) >= 17, f'Expected >= 17, got {len(pcsamp)}'
print('PASS')
"
```

## Discovered Issues (for future session planning)

1. **DRAM metric rename not anticipated**: The `dram__bytes_read` → `dram__bytes_op_read` rename was discovered only through hardware validation. No prior documentation or session plan predicted this. Future plans should explicitly list "DRAM metric name validation" as a separate task.

2. **PM sampling metrics completely different**: All 10 original PM sampling stall-breakdown timeseries do not exist on sm_120. This was discovered during validation. Future plans should scope PM sampling as a separate validation category.

3. **ncu_report installation style**: The module can be a system Python package (not just extras/python). The discovery function needed updating. Future plans should test the ncu_report import BEFORE designing the discovery logic.

4. **Broken symlink in system package**: The ncu_report system package had a broken `libnvperf_host.so` symlink pointing to a build artifact path. This required manual intervention. Future session plans should include "verify ncu_report actually loads a report" as a pre-flight check.
