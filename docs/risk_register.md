# Risk Register

**Project:** ncu-report-skill RTX 5090 Adaptation
**Date:** 2026-06-04

---

## Risk Matrix

| Likelihood \ Impact | Low | Medium | High |
|---|---|---|---|
| **High** | — | R-3 | R-1 |
| **Medium** | R-7 | R-2, R-5 | R-4 |
| **Low** | R-8 | R-6 | — |

---

## Risks

### R-1: Metric Name Incompatibility Between sm_100 and sm_120
- **Likelihood:** High
- **Impact:** High
- **Session:** 3
- **Description:** The curated metric list (100+ names) was validated for sm_100 (B200). NVIDIA changes metric names between compute capability versions. If significant portions of the list are invalid on sm_120, the Python helpers will produce errors or silent wrong results.
- **Evidence:** Historical precedent — metric names changed between Ampere (sm_80), Hopper (sm_90), and Blackwell data-center (sm_100). The sm_100→sm_120 transition has no documented metric migration guide.
- **Mitigation:** Session 3 includes a full metric validation procedure: collect an ncu report on the local 5090, extract `action.metric_names()`, and diff against the current list. Budget time for discovering and mapping renamed metrics.
- **Fallback:** If >30% of metrics are missing, pause Session 3 and create a dedicated metric discovery sub-task using multiple kernel types (compute-bound, memory-bound, tensor-core) to ensure broad metric coverage.
- **Owner:** Session 3 executor

### R-2: Shared Memory Limit Surprises
- **Likelihood:** Medium
- **Impact:** Medium
- **Session:** 1, 3
- **Description:** The local GPU reports 100 KB shared memory per SM and 48 KB default per block. Web sources variously claim 128 KB per SM and 99 KB opt-in per block. The opt-in maximum via `cudaFuncSetAttribute` is unknown until tested.
- **Evidence:** `cudaDeviceProp` reports 102,400 bytes/SM and 49,152 bytes/block. These are runtime defaults, not necessarily hardware maximums. The Blackwell Tuning Guide mentions 128 KB per SM for CC 12.0, which conflicts with the runtime query.
- **Mitigation:** Session 3 includes an explicit test of `cudaFuncSetAttribute(cudaFuncAttributeMaxDynamicSharedMemorySize)` with increasing values to find the true ceiling. Programming guide written in Session 1 uses the conservative 100 KB/SM value with a note that opt-in max is pending validation.
- **Fallback:** If the opt-in max differs from the documented values, update programming guide and analysis dimensions in a targeted fix.
- **Owner:** Session 3 executor

### R-3: tcgen05 / TMEM Not Available on Consumer Blackwell
- **Likelihood:** High
- **Impact:** Medium
- **Session:** 1
- **Description:** The 5th-gen tensor core ISA (tcgen05) and dedicated Tensor Memory (TMEM) are documented for Blackwell architecture broadly, but some features may be restricted to data-center SKUs (B200/B100). If tcgen05 PTX instructions don't compile for sm_120, or TMEM metrics don't appear in ncu output, the tensor core sections need different content.
- **Evidence:** NVIDIA documentation describes tcgen05 as a Blackwell feature without clearly distinguishing consumer vs data-center availability. The CC 12.0 vs 10.0 split suggests they may have different ISA surfaces.
- **Mitigation:** Session 1 includes a compile test of tcgen05 PTX for sm_120. If it fails, rewrite tensor core sections using WMMA/MMA intrinsics that are known to work on consumer GPUs. TMEM validation deferred to Session 3 (metric check).
- **Fallback:** Fall back to documenting CUTLASS/cuBLAS as the recommended tensor core access path if low-level PTX is unavailable.
- **Owner:** Session 1 executor

### R-4: ncu Report Collection Fails or Requires Elevated Privileges
- **Likelihood:** Medium
- **Impact:** High
- **Session:** 3, 4
- **Description:** Nsight Compute on consumer GPUs with a display driver running may require `sudo` or a modprobe configuration to access performance counters. If the local environment doesn't allow profiling, Sessions 3 and 4 (which depend on collecting real reports) are blocked.
- **Evidence:** The existing skill documents this in `reference/09-common-issues.md`. Consumer GPUs with active display servers are more likely to hit this restriction than headless data-center GPUs.
- **Mitigation:** Test ncu collection early in Session 3 (before the full validation procedure). If it fails, apply the documented modprobe fix or use `sudo ncu`.
- **Fallback:** If profiling is completely blocked (e.g., corporate security policy prevents modprobe changes), metric validation can be deferred and the skill ships with the "carried-forward-unverified" annotations.
- **Owner:** Session 3 executor

### R-5: Clock Throttling Under Profiling Distorts Measurements
- **Likelihood:** Medium
- **Impact:** Medium
- **Session:** 4
- **Description:** The RTX 5090 draws 575W under full load. ncu profiling replays kernels many times, which sustains high power draw. If thermal or power throttling kicks in, performance metrics (especially bandwidth and FLOPS) will be lower than theoretical peaks, distorting roofline analysis.
- **Evidence:** This is a known issue with consumer GPUs under extended profiling. The display driver also consumes GPU resources.
- **Mitigation:** Session 4's bandwidth benchmark (Gap G-7) will establish the effective bandwidth under profiling conditions. Document the gap between theoretical and measured bandwidth in the programming guide.
- **Fallback:** If throttling is severe (>25% reduction), add a "profiling conditions" caveat to the report template advising users to measure their own effective peaks.
- **Owner:** Session 4 executor

### R-6: ncu_report Python Module Path Changed in CUDA 13.2
- **Likelihood:** Low
- **Impact:** Medium
- **Session:** 3
- **Description:** The `ncu_report` Python module is shipped inside the Nsight Compute installation directory. Its exact path depends on the CUDA toolkit version and installation method. If the path convention changed in CUDA 13.2 or ncu 2026.2, the existing import pattern will fail.
- **Evidence:** The current skill documents the path as `/usr/local/cuda-XX.X/nsight-compute-YYYY.X.0/extras/python/`. This pattern has been stable but is not guaranteed.
- **Mitigation:** Gap G-6 in Session 3 explicitly validates the import path. The `ncu_utils.py` helper can auto-detect the path using `which ncu` as a starting point.
- **Fallback:** If the path changed, update the documented path and add a fallback detection mechanism to ncu_utils.py.
- **Owner:** Session 3 executor

### R-7: GDDR7 Access Pattern Differences from HBM Are Material
- **Likelihood:** Medium
- **Impact:** Low
- **Session:** 1, 2
- **Description:** The B200 skill's memory access guidance assumes HBM3e characteristics (high bandwidth, stacked memory, multi-bank). GDDR7 has different burst length, bank structure, and latency characteristics. If these differences materially affect profiling interpretation, the memory analysis dimension needs GDDR7-specific guidance.
- **Evidence:** GDDR7 and HBM3e are fundamentally different memory technologies. However, for CUDA profiling purposes, the memory controller abstracts most differences — the metrics (coalescing, sectors/request, L2 hit rate) remain the primary analysis tools regardless of memory type.
- **Mitigation:** Session 1's programming guide rewrite removes HBM-specific content and frames memory guidance around bandwidth ceiling and coalescing quality, which are memory-type-agnostic. If GDDR7-specific patterns emerge during Session 4 validation, they can be added then.
- **Fallback:** Accept that GDDR7-specific guidance is a MAY requirement (O-1 in the project contract) and defer to a future enhancement if needed.
- **Owner:** Session 1 executor

### R-8: Stale Documentation References Survive Adaptation
- **Likelihood:** Low
- **Impact:** Low
- **Session:** All, final check in 4
- **Description:** With 20+ files to update, it's possible for a B200-specific reference, threshold, or metric name to survive in a corner of the documentation that doesn't get checked.
- **Evidence:** This is a standard risk in any large find-and-replace effort.
- **Mitigation:** Session 4 includes a cross-file consistency check using `grep -ri` to find any remaining B200/sm_100 references. Each session also has its own grep-based exit criterion.
- **Fallback:** Any surviving references are trivial to fix in a targeted commit.
- **Owner:** Session 4 executor
