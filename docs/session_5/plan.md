# Session 5 Plan — CUDA 13.3 Tile Kernel Support

## Task 1: Version Bump (CUDA 13.2 → 13.3)

### 1.1 Replace version references
**Files:** `blackwell-cuda-programming.md:8`, `README.md:137`, `reference/04-python-api.md:7,17`, `reference/09-common-issues.md:110-111`, `ENVIRONMENT.md:7`
**Action:** Find-and-replace `13.2` → `13.3` in each file. For path references, replace `cuda-13.2` → `cuda-13.3`.

### 1.2 Verify
**Command:** `grep -rci 'CUDA 13\.2' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs . | grep -v ':0$'`
**Expected:** Empty output.
Also run: `grep -rn '13\.2' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs .` to catch non-"CUDA" prefixed references.

**Commit point:** After task 1 passes.

---

## Task 2: Hardware Validation — Element-wise Tile Kernel

### 2.1–2.3 Write and run tile vector_add
**File:** `profile/validation_run/tile_vector_add.cu` (gitignored)
**Kernel structure:**
```cpp
#include <cuda_tile.h>
using namespace cuda::tile;
namespace ct = cuda::tile;

__tile_global__ void tile_vadd(float* __restrict__ a, float* __restrict__ b, float* __restrict__ c, int n) {
    auto bid = ct::bid();
    // Load tiles from a and b at offset bid * TILE_SIZE
    // Element-wise add
    // Store to c
}
// Launch: tile_vadd<<<N/TILE_SIZE, 1>>>(a, b, c, N);
```
**Compile:** `nvcc -arch=sm_120 -o tile_vadd tile_vector_add.cu`
**Run:** `./tile_vadd` — check output correctness.

### 2.4–2.5 Profile tile kernel
**Command:** `sudo ncu --set full -o tile_vadd_report ./tile_vadd`
**Extract:** Use `ncu --import tile_vadd_report.ncu-rep --csv --page raw` or Python API to extract key metrics.
**Record:** Save metric summary to `profile/validation_run/tile_vadd_metrics.txt`.

### 2.6–2.8 SIMT comparison
**File:** `profile/validation_run/simt_vector_add.cu` (gitignored)
**Profile:** Same ncu flags. Compare occupancy, stalls, memory metrics side by side.
**Document:** Save comparison to `profile/validation_run/simt_vs_tile_comparison.md`.

---

## Task 3: Hardware Validation — Tile GEMM (ct::mma)

### 3.1–3.2 Write and run tile GEMM
**File:** `profile/validation_run/tile_gemm.cu` (gitignored)
**Kernel:** Use `ct::mma()` with appropriate tile shapes for sm_120 tensor cores.
**Verify:** Compare output against CPU reference (tolerance: 1e-2 for BF16).

### 3.3–3.4 Profile and record tensor core metrics
**Command:** `sudo ncu --set full -o tile_gemm_report ./tile_gemm`
**Focus metrics:** `smsp__pipe_tensor_op_hmma_cycles_active.sum`, `smsp__inst_executed_pipe_tensor_op_hmma.sum` and equivalents.
**Record:** Which tensor core metrics have non-zero values for ct::mma.

---

## Task 4: Hardware Validation — Tile Reduction (Atomics)

### 4.1–4.2 Write and run tile reduction
**File:** `profile/validation_run/tile_reduction.cu` (gitignored)
**Kernel:** Use `ct::atomic_add` for parallel reduction to a single output.
**Verify:** Output matches expected sum.

### 4.3–4.4 Profile atomics
**Focus metrics:** Stall reasons related to atomics, atomic throughput counters.
**Record:** Atomic-specific stall signatures for tile kernels.

---

## Task 5: Hardware Validation — TMA and Hints

### 5.1–5.2 Test hint architecture code
**File:** `profile/validation_run/tile_hint_test.cu` (gitignored)
**Test:** Compile kernels with `cutile::hint(1200, occupancy=4)` and `cutile::hint(0, occupancy=4)`.
**Record:** Which codes compile and which are rejected.

### 5.3–5.4 Test TMA
**Add to tile_vadd or GEMM kernel:** `ct::assume_aligned(ptr, 16_ic)` + partition_view + `cutile::hint(arch, allow_tma=true)`.
**Record:** Whether TMA path is triggered (check ncu for TMA-related metrics or lowered instructions).

**Commit point:** After tasks 2–5, commit validation summary (not artifacts) if needed. Validation artifacts stay gitignored.

---

## Task 6: Tile Kernel Programming Guide Section

### 6.1–6.6 Write programming guide content
**File:** `blackwell-cuda-programming.md`
**Insertion point:** After "Special Kernel Types Quick Reference" section, before "Pre-Coding Checklist".
**New section:** `## Tile Kernel Programming Model (CUDA 13.3+)`

Content is written AFTER validation, using real ncu output to ground the "Profiling Tile Kernels" subsection.

### 6.7 Verify
**Commands:**
- `grep -c 'Tile Kernel\|tile kernel\|__tile_global__' blackwell-cuda-programming.md` — must be >= 3
- `grep -c '__restrict__\|assume_aligned\|irange\|partition_view' blackwell-cuda-programming.md` — must be >= 4

**Commit point:** After task 6 passes.

---

## Task 7: Tile Kernel Diagnosis Patterns

### 7.1–7.4 Write 4 patterns
**File:** `reference/06-diagnosis-playbook.md`
**Insertion point:** After Pattern Q (Quantization mismatch), before "Single-User Decode Optimization Checklist".
**Structure:** Each pattern follows pattern→cause→fix with specific ncu metric references from validation.

### 7.5 Verify
**Commands:**
- `grep -c 'tile.*kernel\|Tile.*Kernel\|tile.*pattern\|Tile.*Pattern' reference/06-diagnosis-playbook.md` — must be >= 4
- `grep -c 'atomic.*contention\|atomic.*tile\|tile.*atomic' reference/06-diagnosis-playbook.md` — must be >= 1

---

## Task 8: Analysis Dimension Annotations

### 8.1–8.6 Annotate all 6 dimensions
**File:** `reference/05-analysis-dimensions.md`
**Action:** Add a "**Tile kernel note:**" paragraph at the end of each dimension section.

---

## Task 9: Workflow, Common Issues, Metrics, Harness

### 9.1–9.3 Workflow updates
**File:** `reference/01-workflow.md`
**Action:** Add tile variant to Phase 2, collection note to Phase 3, pattern reference to Phase 5.

### 9.4 Common issues
**File:** `reference/09-common-issues.md`
**Action:** Add tile kernel gotchas section (launch syntax, cross-calling, _ic).
**Verify:** `grep -c 'tile\|Tile\|__tile_global__' reference/09-common-issues.md` — must be >= 2

### 9.5 Metric notes
**File:** `reference/08-rtx5090-metric-names.md`
**Action:** Add tile kernel metric behavior section based on validation data.

### 9.6 Harness template
**File:** `helpers/harness_template.cu`
**Action:** Add `#if 0` guarded tile kernel section after SIMT kernel stub.

**Commit point:** After task 9 passes.

---

## Task 10: SKILL.md and Project Contract

### 10.1 SKILL.md
**File:** `SKILL.md`
**Action:** Add tile kernel mention in skill description or critical lessons.
**Verify:** `grep -c 'tile\|Tile' SKILL.md` — must be >= 1

### 10.2 Project contract
**File:** `docs/project_contract.md`
**Action:** Ensure version 1.1, CUDA 13.3, and "all 5 sessions" are present.
**Verify:** `grep -c '13\.3' docs/project_contract.md` — must be >= 1; `grep -c 'all 5 sessions' docs/project_contract.md` — must be >= 1

### 10.3 Full deterministic check suite
Run all 9 deterministic checks from session contract. All must pass.

**Commit point:** Final commit after all checks pass.
