# Session 3 Gap Resolution Report

## G-1: Max Dynamic Shared Memory Per Block

**Method**: `cudaFuncSetAttribute(kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, N)` with increasing N values.

**Result**:
| Size | Status |
|---|---|
| 49,152 B (48 KB) — default | OK |
| 65,536 B (64 KB) | OK |
| 81,920 B (80 KB) | OK |
| 98,304 B (96 KB) | OK (max opt-in) |
| 102,400 B (100 KB) | FAILED (invalid argument) |
| 131,072 B (128 KB) | FAILED (invalid argument) |

**Conclusion**: Default shared memory per block is 48 KB. Opt-in max via `cudaFuncSetAttribute` is **98,304 bytes (96 KB)**. The full 100 KB/SM (102,400 B from `sharedMemPerMultiprocessor`) is NOT entirely available to a single block — 4 KB is reserved for driver/hardware overhead.

## G-2: Metric Name Compatibility (sm_100 → sm_120)

**Method**: Compiled vector_add kernel with sm_120, collected `ncu --set full --section PmSampling`, extracted `action.metric_names()` (2,383 total metrics).

**Result**: 93/100 curated metrics present (93%).

**Missing metrics — all DRAM with renamed pattern**:
| sm_100 Name | sm_120 Name |
|---|---|
| `dram__bytes_read.sum` | `dram__bytes_op_read.sum` |
| `dram__bytes_read.sum.pct_of_peak_sustained_elapsed` | `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` |
| `dram__bytes_read.sum.per_second` | `dram__bytes_op_read.sum.per_second` |
| `dram__bytes_write.sum` | `dram__bytes_op_write.sum` |
| `dram__bytes_write.sum.pct_of_peak_sustained_elapsed` | `dram__bytes_op_write.sum.pct_of_peak_sustained_elapsed` |
| `dram__sectors_read.sum` | `dram__sectors_op_read.sum` |
| `dram__sectors_write.sum` | `dram__sectors_op_write.sum` |

**Pattern**: `dram__bytes_read` → `dram__bytes_op_read`, `dram__bytes_write` → `dram__bytes_op_write`, `dram__sectors_read` → `dram__sectors_op_read`, `dram__sectors_write` → `dram__sectors_op_write`.

**Stall metrics**: 17/17 (100%) present — no changes needed.

**PM sampling metrics**: The old stall-breakdown timeseries (`pmsampling:smsp__warps_issue_stalled_*.avg`) do not exist on sm_120. Replaced with available hardware-counter timeseries: warp activity, DRAM bandwidth, L1 wavefronts, FMA pipe activity, PCIe throughput, GPC clock.

## G-5: TMEM Metric Availability

**Method**: Searched `action.metric_names()` output for any metric containing "tmem" (case-insensitive).

**Result**: **Zero TMEM metrics found** on RTX 5090. TMEM (Tensor Memory) is a data-center Blackwell feature not exposed on consumer sm_120 GPUs.

## G-6: ncu_report Import Path

**Method**: `python3 -c "import ncu_report; print(ncu_report.__file__)"`

**Result**: `/usr/lib/python3.14/site-packages/ncu_report/__init__.py`

The module is installed as a **system Python package** (not under the CUDA extras/python directory). It contains:
- `__init__.py` (pure Python wrapper)
- `_ncu_report.so` (native extension)
- `libnvperf_host.so` (symlink to ncu installation directory)

No `PYTHONPATH` manipulation is needed when installed this way. The `_locate_ncu_report()` fallback was updated to also detect package directories (`ncu_report/__init__.py`), not just single-file modules.

## G-8: Shared Memory Carveout Options

**Method**: Tested `cudaFuncSetCacheConfig` with all four values and `cudaFuncSetAttribute` with `cudaFuncAttributePreferredSharedMemoryCarveout` at 0%, 25%, 50%, 75%, 100%.

**Result**: All configurations accepted.

| Config | Status |
|---|---|
| `cudaFuncCachePreferNone` | OK |
| `cudaFuncCachePreferShared` | OK |
| `cudaFuncCachePreferL1` | OK |
| `cudaFuncCachePreferEqual` | OK |
| Carveout 0% | OK |
| Carveout 25% | OK |
| Carveout 50% | OK |
| Carveout 75% | OK |
| Carveout 100% | OK |
