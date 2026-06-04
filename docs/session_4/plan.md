# Session 4 Implementation Plan

**Source:** `docs/session_4/tasks.md`, `docs/session_4/design.md`, `docs/session_4/specs/`

---

## Task 1: DRAM & PM Sampling Metric Fix-Forward

### 1.1–1.3: Rename DRAM metrics + fix PM sampling

**Pre-test (verify broken state):**
```bash
grep -rn 'dram__bytes_read\b\|dram__bytes_write\b\|dram__sectors_read\b\|dram__sectors_write\b' \
  --include='*.md' --include='*.py' --exclude-dir=docs . | wc -l
# Expected: ~22 (confirms old names exist)
```

**Implementation:**
For each of these 10 files, apply find-and-replace:
- `SKILL.md:85` — 1 occurrence
- `blackwell-cuda-programming.md:316-317` — 2 occurrences
- `reference/01-workflow.md:215` — 1 occurrence
- `reference/03-collection.md:111` — 1 occurrence
- `reference/04-python-api.md:44,221` — 2 occurrences + PM sampling fix at :77
- `reference/05-analysis-dimensions.md:230-233,261` — 5 occurrences
- `reference/06-diagnosis-playbook.md:130,331,362` — 3 occurrences
- `reference/07-report-template.md:68` — 1 occurrence
- `reference/08-rtx5090-metric-names.md:26,65-71` — 8 occurrences + PM sampling section :187-200
- `reference/09-common-issues.md:230` — 1 occurrence

Rename patterns:
- `dram__bytes_read` → `dram__bytes_op_read`
- `dram__bytes_write` → `dram__bytes_op_write`
- `dram__sectors_read` → `dram__sectors_op_read`
- `dram__sectors_write` → `dram__sectors_op_write`

For PM sampling in reference/08, replace old stall-breakdown timeseries with sm_120 hardware-counter names from Session 3 validation.

### 1.4–1.5: Verification

```bash
# Zero old DRAM names
grep -rn 'dram__bytes_read\b\|dram__bytes_write\b\|dram__sectors_read\b\|dram__sectors_write\b' \
  --include='*.md' --include='*.py' --exclude-dir=docs .
# Expected: empty

# ncu_utils.py still correct
grep -c 'dram__bytes_op_read\|dram__bytes_op_write' helpers/ncu_utils.py
# Expected: >= 2
```

**Commit point after Task 1.**

---

## Task 2: Precision-Specific Profiling Recipes

### 2.1–2.5: Add recipes to blackwell-cuda-programming.md

**Pre-test:**
```bash
grep -c 'Profiling.*Recipe\|recipe.*profil' blackwell-cuda-programming.md
# Expected: 0 (recipes don't exist yet)
```

**Implementation:**
Insert new subsection `### Precision-Specific Profiling Recipes` after line ~321 (after the decode signal table, before "Why This Document Exists").

Content for each recipe follows the template from spec. Use RTX 5090 values:
- BF16: 209.5 TFLOPS dense, tensor pipe metric
- FP8: 419 TFLOPS dense, FP8 sub-pipe
- INT8: 838 TOPS, INT8 pipe
- FP4: 1,676 TOPS dense (library-only caveat)

Cross-precision comparison: table format, same kernel, same input, diff metrics.

### 2.6: Verification

```bash
grep -c 'Profiling BF16\|Profiling FP8\|Profiling INT8\|Profiling FP4' blackwell-cuda-programming.md
# Expected: >= 4
```

**Commit point after Task 2.**

---

## Task 3: Framework Profiling Walkthrough

### 3.1–3.3: Expand Phase 2.5 in reference/01-workflow.md

**Pre-test:**
```bash
grep -c 'action mapping\|VRAM budget\|VRAM Budget' reference/01-workflow.md
# Expected: 0
```

**Implementation:**
Insert three new subsections after "What to do with the results" (after line ~155, before Phase 3):

1. `### Framework-specific action mapping` — Table with 4 columns (finding, TRT-LLM, vLLM, PyTorch), ~8-10 rows
2. `### RTX 5090 VRAM budget planning` — Formulas + example table for 7B/13B/70B
3. `### Expanded kernel naming patterns` — Expand existing bullet list into a structured reference table

### 3.4: Verification

```bash
grep -c 'TensorRT-LLM\|vLLM\|PyTorch' reference/01-workflow.md
# Expected: significant increase from current count
```

**Commit point after Task 3.**

---

## Task 4: Decode Optimization Checklist

### 4.1–4.3: Add checklist to reference/06-diagnosis-playbook.md

**Pre-test:**
```bash
grep -c 'Decode Optimization Checklist' reference/06-diagnosis-playbook.md
# Expected: 0
```

**Implementation:**
Insert `## Single-User Decode Optimization Checklist (RTX 5090)` after Pattern Q section (before "Ranking template for the final report" at line ~430).

Write ~16 steps in 3 phases per spec. Each step uses corrected _op_ DRAM names. Reference Patterns O, P, Q by name.

### 4.4–4.5: Verification

```bash
grep -c 'Decode Optimization' reference/06-diagnosis-playbook.md
# Expected: >= 1

# No old DRAM names in the new checklist
grep -A 100 'Decode Optimization' reference/06-diagnosis-playbook.md | grep -c 'dram__bytes_read\b'
# Expected: 0

# Pattern references
grep -A 100 'Decode Optimization' reference/06-diagnosis-playbook.md | grep -c 'Pattern [OPQ]'
# Expected: >= 3
```

**Commit point after Task 4.**

---

## Task 5: Gap Resolutions

### 5.1–5.2: G-4 Cluster Launch Test

**Implementation:**
Write `/tmp/cluster_test.cu`:
```c
__global__ void cluster_kernel() { /* minimal */ }
int main() {
    cudaLaunchConfig_t config = {};
    cudaLaunchAttribute attr;
    attr.id = cudaLaunchAttributeClusterDimension;
    attr.val.clusterDim = {2, 1, 1};
    config.attrs = &attr; config.numAttrs = 1;
    config.gridDim = {2, 1, 1}; config.blockDim = {128, 1, 1};
    cudaError_t err = cudaLaunchKernelEx(&config, cluster_kernel);
    printf("Result: %s\n", cudaGetErrorString(err));
}
```
Compile: `nvcc -arch=sm_120 -o /tmp/cluster_test /tmp/cluster_test.cu`
Run and capture result. Document in reference/09-common-issues.md.

### 5.3–5.4: G-7 Bandwidth Measurement

**Implementation:**
Write `/tmp/bw_test.cu`:
- Device-to-device copy kernel using float4 (128-bit loads/stores)
- Buffer size: 256 MB per array (read + write)
- Warm-up pass, then profiled pass

Compile: `nvcc -arch=sm_120 -o /tmp/bw_test /tmp/bw_test.cu`
Profile: `ncu --set full -o /tmp/bw_report /tmp/bw_test`
Extract: `dram__bytes_op_read.sum.per_second`, `dram__bytes_op_write.sum.per_second`
Document measured vs theoretical in reference/09-common-issues.md.

**Commit point after Task 5.**

---

## Task 6: End-to-End Validation

### 6.1: Phase 0 — Setup
```bash
mkdir -p profile/validation_run/reports
echo 'profile/validation_run/' >> .gitignore
```

### 6.2: Phase 1 — Environment check
```bash
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader
nvcc --version
ncu --version
python3 -c "import ncu_report; print('OK')"
```

### 6.3: Phase 2 — Compile
```bash
nvcc -arch=sm_120 -lineinfo -o profile/validation_run/harness helpers/harness_template.cu
```

### 6.4: Phase 3 — Collect
```bash
ncu --set full --section PmSampling \
    -o profile/validation_run/reports/full \
    profile/validation_run/harness

ncu --set source --section SourceCounters \
    -o profile/validation_run/reports/source \
    profile/validation_run/harness
```

### 6.5: Phase 4 — Parse
```bash
python3 helpers/analyze_reports.py profile/validation_run/reports/full.ncu-rep
python3 helpers/extract_stall_hotspots.py profile/validation_run/reports/source.ncu-rep
python3 helpers/plot_timeline.py profile/validation_run/reports/full.ncu-rep
```

### 6.6: Phase 5 — Diagnose
Apply six-dimension framework to output. Verify each dimension produces values.

### 6.7: Phase 6 — Report
Generate `profile/validation_run/REPORT.md` following `reference/07-report-template.md`.

**No commit for Task 6** (validation artifacts are gitignored).

---

## Task 7: Cross-File Consistency & Cleanup

### 7.1–7.4: Final sweep
```bash
# B200 sweep
grep -rci 'B200\|b200\|sm_100\|sm100' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs . | grep -v ':0$'

# Hardware consistency (spot check)
grep -rn '170 SM\|48 warp\|1.792\|1,792\|1.8 TB\|96 MB L2\|32 GB\|100 KB shared' --include='*.md' --exclude-dir=docs . | head -20

# Metric consistency
grep -rn 'dram__bytes_read\b\|dram__bytes_write\b' --include='*.md' --include='*.py' --exclude-dir=docs .
# Expected: empty (only _op_ variants)
```

Remove "unverified on sm_120" caveat from reference/08-rtx5090-metric-names.md header.

**Commit point after Task 7.**
