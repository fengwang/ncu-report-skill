# Session 3 Implementation Plan

## Task 1: Hardware Validation Setup

### 1.1 Verify ncu_report import (G-6)
```bash
python3 -c "import ncu_report; print('OK:', ncu_report.__file__)"
```
Expected: `OK: /usr/lib/python3.14/site-packages/ncu_report/__init__.py`

### 1.2 Write and compile temp kernel
Write `/tmp/vec_add_sm120.cu`:
```cuda
#include <cstdio>
__global__ void vec_add(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}
int main() {
    const int N = 1024;
    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, N*sizeof(float));
    cudaMalloc(&d_b, N*sizeof(float));
    cudaMalloc(&d_c, N*sizeof(float));
    vec_add<<<(N+255)/256, 256>>>(d_a, d_b, d_c, N);
    cudaDeviceSynchronize();
    cudaFree(d_a); cudaFree(d_b); cudaFree(d_c);
    printf("OK\n");
    return 0;
}
```
Compile: `nvcc -arch=sm_120 -lineinfo -o /tmp/vec_add_sm120 /tmp/vec_add_sm120.cu`

### 1.3 Collect ncu report
```bash
ncu --set full --section PmSampling -o /tmp/sm120_report /tmp/vec_add_sm120
```
May need `sudo`. If so: `sudo ncu --set full --section PmSampling -o /tmp/sm120_report /tmp/vec_add_sm120`

### 1.4 Extract metric names
```python
import ncu_report
report = ncu_report.load_report('/tmp/sm120_report.ncu-rep')
rng = report.range_by_idx(0)
action = rng.action_by_idx(0)
names = sorted(action.metric_names())
with open('/tmp/sm120_metrics.txt', 'w') as f:
    for n in names: f.write(n + '\n')
print(f'Total: {len(names)}')
```

**Commit point: None (validation data only, not deliverables)**

## Task 2: Metric Validation (G-2)

### 2.1-2.4 Diff and categorize
Python script to diff B200_KEY_METRICS against sm120_metrics.txt.
Separately check STALL_METRICS and DEFAULT_METRICS lists.
Categorize each metric as: present / removed / new.

### 2.5 Check threshold
If <80% present: STOP and escalate per session plan risk mitigation.

**Commit point: None (analysis only)**

## Task 3: Gap Experiments (G-1, G-5, G-8)

### 3.1 G-1: Max shared memory
Write `/tmp/shmem_test.cu` that tests increasing dynamic shared memory sizes.
Expected result: up to 100 KB (102400 bytes) since sharedMemPerMultiprocessor = 102400.

### 3.2 G-5: TMEM metrics
```bash
grep -i tmem /tmp/sm120_metrics.txt
```

### 3.3 G-8: Carveout options
Write `/tmp/carveout_test.cu` that tests `cudaFuncSetCacheConfig` with various values.

**Commit point: None (gap data only)**

## Task 4: Update ncu_utils.py

### 4.1 Rename variable
Replace `B200_KEY_METRICS` with `RTX5090_KEY_METRICS`.

### 4.2 Replace metric list content
Use validated metric names from Task 2. Annotate unverified metrics.

### 4.3 Update _locate_ncu_report()
- Add check for `ncu_report/__init__.py` alongside `ncu_report.py`
- Update hardcoded candidate path from `2026.1.0` to glob pattern
- Update docstring PYTHONPATH example

### 4.4 Update comments
Remove all B200/sm_100 references.

Test: `python3 -c "from ncu_utils import RTX5090_KEY_METRICS; print(len(RTX5090_KEY_METRICS))"`

**Commit point: after Task 4 passes self-check**

## Task 5: Update analyze_reports.py

### 5.1 Update import
`from ncu_utils import B200_KEY_METRICS` → `from ncu_utils import RTX5090_KEY_METRICS`

### 5.2 Add constants
```python
RTX5090_PEAK_BW_GBS = 1792
RTX5090_PEAK_FP32_TFLOPS = 104.8
RTX5090_PEAK_BF16_TFLOPS = 209.51
```

### 5.3 Update references
Replace all `B200_KEY_METRICS` usages with `RTX5090_KEY_METRICS`.
Update docstring.

Test: `grep -c '1792\|1.792' helpers/analyze_reports.py` returns >= 1

**Commit point: after Task 5**

## Task 6-7: Update stall + timeline scripts

Update metric lists based on validation results from Task 2.
These scripts have no B200 string references in code, only in metric names (which are the same).
Only change metric lists if validation found differences.

**Commit point: after Tasks 6-7**

## Task 8: Update harness_template.cu

Change: `arch=compute_100,code=sm_100` → `arch=compute_120,code=sm_120`

Test: Verify no sm_100/compute_100 references remain.
Note: Template won't compile as-is (stub kernel) — this is by design.

## Task 9: Update helpers/README.md

Update compile example, metric list variable name, PYTHONPATH.

## Task 10: Fix stale filename references

In SKILL.md and README.md, replace `08-b200-metric-names.md` with `08-rtx5090-metric-names.md`.

**Commit point: after Tasks 8-10**

## Task 11: Final Verification

Run all deterministic checks:
```bash
grep -c 'B200_KEY_METRICS' helpers/ncu_utils.py                    # must be 0
grep -rci 'B200\|b200\|sm_100\|sm100' helpers/ | grep -v ':0$'     # must be empty
grep -c '1792\|1.792\|1.8' helpers/analyze_reports.py               # must be >= 1
grep '08-b200-metric-names' SKILL.md README.md                      # must be empty
```
